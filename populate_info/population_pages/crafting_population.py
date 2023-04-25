from flask import redirect, render_template, request, session, url_for

import populate_info.resources as r
from populate_info.group_utils import (
    get_group_crafting_info, maybe_group_toggle_update_saved, maybe_write_category_to_group)
from populate_info.json_utils import write_json_category_to_file
from populate_info.navigation_utils import either_move_next_category_or_repeat
from populate_info.population_pages import item_blueprint

HTML_TO_JSON = {
    # Slots
    "cs1": "1", "cs2": "2", "cs3": "3",
    "cs4": "4", "cs5": "5", "cs6": "6",
    "cs7": "7", "cs8": "8", "cs9": "9",
    # Remaining values
    "number-created": r.CRAFTING_N_CREATED_J_KEY,
    "small-grid": r.CRAFTING_SMALL_GRID_J_KEY,
    "flexible-positioning": r.CRAFTING_RELATIVE_POSITIONING_J_KEY
}
JSON_TO_HTML = {value: key for key, value in HTML_TO_JSON.items()}


def crafting_json_to_html_ids(json_data: dict) -> dict:
    result_data = {
        "to-fill":
            {JSON_TO_HTML[slot]: item for slot, item in json_data[r.CRAFTING_SLOTS_J_KEY].items()} |
            {JSON_TO_HTML[r.CRAFTING_N_CREATED_J_KEY]: json_data[r.CRAFTING_N_CREATED_J_KEY]},
        "to-mark-checked": [
            f"small-grid-{'yes' if json_data[r.CRAFTING_SMALL_GRID_J_KEY] else 'no'}",
            f"flexible-positioning-"
            f"{'yes' if json_data[r.CRAFTING_RELATIVE_POSITIONING_J_KEY] == 'flexible' else 'no'}"]}
    # TODO - show which continue button should be pressed!
    return result_data


@item_blueprint.route("/crafting/<item_name>", methods=["GET", "POST"])
def crafting(item_name):
    """ Handles populating the crafting obtainment method. """
    if request.method == "GET":
        return render_template(
            "add_item/crafting.html",
            item_name=item_name,
            group_name=session.get(r.GROUP_NAME_SK, ""),
            is_toggle_selected=session.get(r.USE_GROUP_VALUES_SK, False),
            group_info=crafting_json_to_html_ids(get_group_crafting_info(session[r.GROUP_NAME_SK], item_name)),
            # TODO - temporarily on
            show_group=True)

    if maybe_group_toggle_update_saved(session, request.form):
        return redirect(url_for("add.crafting", item_name=item_name))

    data = {
        r.CRAFTING_SLOTS_J_KEY: {},
        r.CRAFTING_N_CREATED_J_KEY: int(request.form["number-created"]),
        r.CRAFTING_RELATIVE_POSITIONING_J_KEY:
            "flexible" if request.form["flexible-positioning"] == "flexible-yes" else "strict",
        r.CRAFTING_SMALL_GRID_J_KEY: request.form["small-grid"] == "grid-yes"
    }
    has_an_item = False
    for i in range(1, 10):
        if request.form[f"cs{i}"] != "":
            has_an_item = True
            data[r.CRAFTING_SLOTS_J_KEY][f"{i}"] = request.form[f"cs{i}"]

    # TODO - sanity check that there is at least one crafting information.
    write_json_category_to_file(item_name, r.CRAFTING_CAT_KEY, data)
    # TODO (add to github too) - replace all session[] with session.get with default string.
    maybe_write_category_to_group(session[r.GROUP_NAME_SK], item_name, r.CRAFTING_CAT_KEY, data)

    return either_move_next_category_or_repeat(item_name, "add.crafting", request.form)

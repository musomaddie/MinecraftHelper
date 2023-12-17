import typing

from flask import redirect, request, session, url_for

import populate_info.resources as r
from populate_info.group_utils import (
    maybe_group_toggle_update_saved, get_next_group_data,
    get_button_choice)
from populate_info.navigation_utils import either_move_next_category_or_repeat
from populate_info.population_pages import item_blueprint
from populate_info.population_pages.shared_behaviour import render_population_template, save_values_to_file

KEY_N_CREATED = "number created"
KEY_SMALL_GRID = "works in smaller grid"
KEY_RELATIVE_POSITIONING = "relative positioning"
KEY_SLOTS = "slots"
HTML_TO_JSON = {
    # Slots
    "cs1": "1", "cs2": "2", "cs3": "3",
    "cs4": "4", "cs5": "5", "cs6": "6",
    "cs7": "7", "cs8": "8", "cs9": "9",
    # Remaining values
    "number-created": KEY_N_CREATED,
    "small-grid": KEY_SMALL_GRID,
    "flexible-positioning": KEY_RELATIVE_POSITIONING
}
JSON_TO_HTML = {value: key for key, value in HTML_TO_JSON.items()}


def crafting_json_to_html_ids(
        group_data: typing.Union[dict, list], item_data: typing.Union[dict, list]) -> dict:
    if len(group_data) == 0:
        return {}
    data_to_populate = get_next_group_data(group_data, item_data)
    result_data = {
        "to-fill":
            {JSON_TO_HTML[slot]: item for slot, item in data_to_populate[KEY_SLOTS].items()} |
            {JSON_TO_HTML[KEY_N_CREATED]: data_to_populate[KEY_N_CREATED]},
        "to-mark-checked": [
            f"small-grid-{'yes' if data_to_populate[KEY_SMALL_GRID] else 'no'}",
            f"flexible-positioning-"
            f"{'yes' if data_to_populate[KEY_RELATIVE_POSITIONING] == 'flexible' else 'no'}"],
        "button-choice": get_button_choice(group_data, item_data)
    }

    # TODO - show which continue button should be pressed!
    return result_data


@item_blueprint.route("/crafting/<item_name>", methods=["GET", "POST"])
def crafting(item_name):
    """ Handles populating the crafting obtainment method. """
    group_name = session.get(r.SK_GROUP_NAME, "")
    if request.method == "GET":
        return render_population_template(
            "add_item/crafting.html",
            item_name,
            group_name,
            r.CK_CRAFTING,
            crafting_json_to_html_ids)

    if maybe_group_toggle_update_saved(session, request.form):
        return redirect(url_for("add.crafting", item_name=item_name))

    data = {
        KEY_SLOTS: {},
        KEY_N_CREATED: int(request.form["number-created"]),
        KEY_RELATIVE_POSITIONING:
            "flexible" if request.form["flexible-positioning"] == "flexible-yes" else "strict",
        KEY_SMALL_GRID: request.form["small-grid"] == "grid-yes"
    }
    has_an_item = False
    for i in range(1, 10):
        if request.form[f"cs{i}"] != "":
            has_an_item = True
            data[KEY_SLOTS][f"{i}"] = request.form[f"cs{i}"]

    # TODO - sanity check that there is at least one crafting information.
    save_values_to_file(item_name, r.CK_CRAFTING, data)

    return either_move_next_category_or_repeat(item_name, "add.crafting", request.form)

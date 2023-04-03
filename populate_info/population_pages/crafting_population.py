from flask import render_template, request, redirect, url_for, session

import populate_info.resources as r
from populate_info.group_utils import maybe_group_toggle_update_saved, get_group_crafting_info
from populate_info.population_pages import item_blueprint

HTML_TO_JSON = {
    # Slots
    "cs1": "1", "cs2": "2", "cs3": "3",
    "cs4": "4", "cs5": "5", "cs6": "6",
    "cs7": "7", "cs8": "8", "cs9": "9",
    # Remaining values
    "number_created": r.CRAFTING_N_CREATED_J_KEY,
    "works_in_four_cbox": r.CRAFTING_SMALL_GRID_J_KEY,
    "flexible_positioning_cbox": r.CRAFTING_RELATIVE_POSITIONING_J_KEY
}
JSON_TO_HTML = {value: key for key, value in HTML_TO_JSON.items()}


def crafting_json_to_html_ids(json_data: dict) -> dict:
    result_data = {"to_fill":
                       {JSON_TO_HTML[slot]: item for slot, item in json_data[r.CRAFTING_SLOTS_J_KEY].items()} |
                       {JSON_TO_HTML[r.CRAFTING_N_CREATED_J_KEY]: json_data[r.CRAFTING_N_CREATED_J_KEY]},
                   "to_mark_checked": []}
    # TODO - to mark result data
    if json_data[r.CRAFTING_SMALL_GRID_J_KEY]:
        result_data["to_mark_checked"].append("works_in_four_cbox")
    if json_data[r.CRAFTING_RELATIVE_POSITIONING_J_KEY] == "flexible":
        result_data["to_mark_checked"].append("flexible_positioning_cbox")
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
            # TODO - temporarily on
            group_info=crafting_json_to_html_ids(get_group_crafting_info(session[r.GROUP_NAME_SK])),
            show_group=True)

    if maybe_group_toggle_update_saved(session, request.form):
        return redirect(url_for("add.crafting", item_name=item_name))

    # Remaining steps from here:
    # 1. Retrieve the data from the form.
    #       Sanity check and complain if the crafting grid has NO information.
    # 2. Save the data to JSON. (item and group).
    # 3. Return possibliy move on.

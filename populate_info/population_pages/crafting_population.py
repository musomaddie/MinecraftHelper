from flask import render_template, request, redirect, url_for, session

import populate_info.resources as r
from populate_info.group_utils import maybe_group_toggle_update_saved
from populate_info.population_pages import item_blueprint

SLOTS_HTML_TO_JSON = {
    "cs1": "1", "cs2": "2", "cs3": "3",
    "cs4": "4", "cs5": "5", "cs6": "6",
    "cs7": "7", "cs8": "8", "cs9": "9"}
SLOTS_JSON_TO_HTML = {value: key for key, value in SLOTS_HTML_TO_JSON.items()}

OPTIONS_HTML_TO_JSON = {
    "number_created": "number created",
    "works_in_four_cbox": "works in smaller grid",
    "flexible_positioning_cbox": "relative positioning"}
OPTIONS_JSON_TO_HTML = {value: key for key, value in OPTIONS_HTML_TO_JSON.items()}


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
            show_group=True)

    if maybe_group_toggle_update_saved(session, request.form):
        return redirect(url_for("add.crafting", item_name=item_name))

    # Remaining steps from here:
    # 1. Retrieve the data from the form.
    #       Sanity check and complain if the crafting grid has NO information.
    # 2. Save the data to JSON. (item and group).
    # 3. Return possibliy move on.

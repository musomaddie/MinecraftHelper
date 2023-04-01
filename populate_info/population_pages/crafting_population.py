from flask import render_template, request, redirect, url_for, session

from populate_info.group_utils import maybe_group_toggle_update_saved
from populate_info.population_pages import item_blueprint


@item_blueprint.route("/crafting/<item_name>", methods=["GET", "POST"])
def crafting(item_name):
    """ Handles populating the crafting obtainment method. """
    if request.method == "GET":
        return render_template(
            "add_item/crafting.html",
            item_name=item_name,
            # TODO - temporarily on
            is_toggle_selected=True,
            show_group=True)

    if maybe_group_toggle_update_saved(session, request.form):
        return redirect(url_for("add.crafting", item_name=item_name))

    # Remaining steps from here:
    # 1. Retrieve the data from the form.
    # 2. Save the data to JSON. (item and group).
    # 3. Return possibliy move on.

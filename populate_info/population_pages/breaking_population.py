from flask import redirect, render_template, request, session, url_for

import populate_info.resources as r
from populate_info.group_utils import maybe_group_toggle_update_saved
from populate_info.population_pages import item_blueprint


@item_blueprint.route("/breaking/<item_name>", methods=["GET", "POST"])
def breaking(item_name):
    """ Handles populating the breaking obtainment method."""
    if request.method == "GET":
        return render_template(
            "add_item/breaking.html",
            item_name=item_name,
            group_name=session[r.GROUP_NAME_SK],
            is_toggle_selected=session.get(r.USE_GROUP_VALUES_SK, False),
            # TODO - temporarily on for testing!
            show_group=True)

    if maybe_group_toggle_update_saved(session, request.form):
        return redirect(url_for("add.breaking", item_name=item_name))

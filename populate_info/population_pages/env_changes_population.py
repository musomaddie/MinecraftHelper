from flask import render_template, session, request, redirect, url_for

import populate_info.resources as r
from populate_info.group_utils import maybe_group_toggle_update_saved
from populate_info.navigation_utils import either_move_next_category_or_repeat
from populate_info.population_pages import item_blueprint


@item_blueprint.route("/env_changes/<item_name>", methods=["GET", "POST"])
def env_changes(item_name):
    if request.method == "GET":
        return render_template(
            "add_item/env_changes.html",
            item_name=item_name,
            is_toggle_selected=session.get(r.USE_GROUP_VALUES_SK, ""),
            show_group=False
        )

    if maybe_group_toggle_update_saved(session, request.form):
        return redirect(url_for("add.env_changes", item_name=item_name))

    # ID is "change_text"

    print(request.form)
    return either_move_next_category_or_repeat(item_name, "add.env_changes", request.form)

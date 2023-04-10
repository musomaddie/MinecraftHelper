from flask import render_template, session

import populate_info.resources as r
from populate_info.population_pages import item_blueprint


@item_blueprint.route("/env_changes/<item_name>", methods=["GET", "POST"])
def env_changes(item_name):
    return render_template(
        "add_item/env_changes.html",
        is_toggle_selected=session.get(r.USE_GROUP_VALUES_SK, ""),
        show_group=False
    )

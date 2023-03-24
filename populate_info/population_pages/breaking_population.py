from flask import render_template, session

import populate_info.resources as r
from populate_info.population_pages import item_blueprint


@item_blueprint.route("/breaking/<item_name>", methods=["GET"])
def breaking(item_name):
    """ Handles populating the breaking obtainment method."""
    return render_template(
        "add_item/breaking.html",
        item_name=item_name,
        is_toggle_selected=session.get(r.USE_GROUP_VALUES_SK, False)
    )

# item_name = item_name,
# item_url = r.get_item_url(item_name),
# group_name = group_name,
# is_toggle_selected = session.get(r.USE_GROUP_VALUES_SK, True),
# group_categories = r.category_names_to_html_ids(get_group_categories(group_name)),
# # Temporarily on for testing TODO
# show_group = True)

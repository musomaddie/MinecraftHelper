""" Python aspects for saving information about items which are naturally generated. """
from flask import request, render_template, session

import populate_info.resources as r
from populate_info.group_utils import should_show_group
from populate_info.population_pages import item_blueprint


@item_blueprint.route("/natural_generation/<item_name>", methods=["GET"])
def natural_generation(item_name):
    """ Displays and processes the natural generation html page. """
    group_name = session.get(r.GROUP_NAME_SK, "")
    if request.method == "GET":
        return render_template(
            "add_item/natural_generation.html",
            item_name=item_name,
            group_name=group_name,
            is_toggle_selected=session.get(r.USE_GROUP_VALUES_SK, False),
            group_info={},
            show_group=should_show_group(group_name)
        )

from flask import render_template

from populate_info.population_pages import item_blueprint


@item_blueprint.route("/breaking/<item_name>", methods=["GET"])
def breaking(item_name):
    """ Handles populating the breaking obtainment method."""
    return render_template("add_item/breaking.html")

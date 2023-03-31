from flask import render_template

from populate_info.population_pages import item_blueprint


@item_blueprint.route("/crafting/<item_name>", methods=["GET", "POST"])
def crafting(item_name):
    return render_template(
        "add_item/crafting.html", item_name=item_name,
        # TODO - temporarily on
        is_toggle_selected=True,
        show_group=True)

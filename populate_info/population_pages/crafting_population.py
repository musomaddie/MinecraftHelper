from populate_info.population_pages import item_blueprint


@item_blueprint.route("/crafting/<item_name>", methods=["GET", "POST"])
def crafting(item_name):
    return "I am crafting"

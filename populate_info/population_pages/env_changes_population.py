from populate_info.population_pages import item_blueprint


@item_blueprint.route("/env_changes/<item_name>", methods=["GET", "POST"])
def env_changes(item_name):
    print("hello I am here")
    return f"Hello - {item_name}!"
    pass

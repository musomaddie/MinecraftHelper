""" python flask code for entering basic population information for blocks. """
from flask import redirect, render_template, request, session, url_for

from populate_info.item import item_factory
from populate_info.item.item import Item
from populate_info.population_pages import item_blueprint


@item_blueprint.route("/add_item/<item_name>", methods=["GET", "POST"])
def start_adding_item(item_name):
    """
    Start adding data for this item.

    :param item_name: the name of the item to be added.
    """
    item = item_factory.create(item_name)

    if "current_item" in session and session["current_item"]["name"] == item_name:
        # If the session item hasn't changed then restore it.
        item = item_factory.create_from_dictionary(session["current_item"])
    # Reset the session item as it might have changed.
    session["current_item"] = item

    if request.method == "GET":
        return render_template(
            "add_item/start.html",
            item_name=item_name,
            item_url=item.get_url(),
            group_name=item.group.name,
            is_toggle_selected=item.group.use_group_values,
            group_categories=item.group.categories_html_ids(),
            show_group=item.group.should_show_group())

    # Update the group name and reload the page (if applicable).
    if "group-name-btn" in request.form:
        item.change_group(request.form["group-name"])
        session["current_item"] = item
        return redirect(url_for("add.start_adding_item", item_name=item_name))

    if item.group.check_toggle_selected(request.form):
        return redirect(url_for("add.start_adding_item", item_name=item_name))

    methods = []
    if "breaking" in request.form.keys():
        methods.append("add.breaking")
    if "crafting" in request.form.keys():
        methods.append("add.crafting")
    if "env-changes" in request.form.keys():
        methods.append("add.env_changes")
    session["methods"] = methods

    item.create_json_file()
    item.group.add_current_item_to_json()
    return item.move_to_next_category()


@item_blueprint.route("/")
def start():
    """ Route to start adding blocks with the next applicable item if non is given. """
    session.clear()
    return redirect(url_for("add.start_adding_item", item_name=Item.get_next_item()))

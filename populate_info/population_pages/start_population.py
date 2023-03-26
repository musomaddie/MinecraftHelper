from flask import redirect, render_template, request, session, url_for

import populate_info.resources as r
from populate_info.group_utils import (get_group_categories, maybe_group_toggle_update_saved, update_group,
    write_group_data_to_json)
from populate_info.json_utils import get_next_item, create_json_file
from populate_info.navigation_utils import move_next_category
from populate_info.population_pages import item_blueprint


@item_blueprint.route("/add_item/<item_name>", methods=["GET", "POST"])
def start_adding_item(item_name):
    """
    Start adding data for this item.

    :param item_name:
    """
    item_file_name = r.get_item_fn(item_name)
    # Don't save to the JSON file until the end, use session for now.
    session[r.CUR_ITEM_SK] = item_name
    # Temporarily set for testing - TODO
    session[r.GROUP_NAME_SK] = "TESTING_GROUP"
    # TODO: add corresponding boolean for group name.
    group_name = session.get(r.GROUP_NAME_SK, "")

    # Return basic page if this is a get request!!
    if request.method == "GET":
        return render_template(
            "add_item/start.html",
            item_name=item_name,
            item_url=r.get_item_url(item_name),
            group_name=group_name,
            is_toggle_selected=session.get(r.USE_GROUP_VALUES_SK, True),
            group_categories=r.category_names_to_html_ids(get_group_categories(group_name)),
            # Temporarily on for testing TODO
            show_group=True)
        # show_group=should_show_group(group_name))

    # Update group name and reload this page (if applicable).
    if "group_name_btn" in request.form:
        new_group_name = request.form["group_name"]
        update_group(group_name, new_group_name, item_name)
        session[r.GROUP_NAME_SK] = new_group_name
        return redirect(url_for("add.start_adding_item", item_name=item_name))

    if maybe_group_toggle_update_saved(session, request.form):
        return redirect(url_for("add.start_adding_item", item_name=item_name))

    methods = []
    if "breaking" in request.form.keys():
        methods.append("add.breaking")
    session[r.METHOD_LIST_SK] = methods

    create_json_file(item_name)
    write_group_data_to_json(item_name, group_name)
    return move_next_category(item_name, methods)


@item_blueprint.route("/")
def start():
    return redirect(url_for("add.start_adding_item", item_name=get_next_item()))

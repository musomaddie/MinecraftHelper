from flask import redirect, render_template, request, session, url_for

import populate_info.resources as r
from populate_info.group_utils import (
    get_group_categories, maybe_group_toggle_update_saved, update_group,
    write_group_name_to_item_json, should_show_group)
from populate_info.json_utils import create_json_file, get_next_item
from populate_info.navigation_utils import move_next_category
from populate_info.population_pages import item_blueprint


@item_blueprint.route("/add_item/<item_name>", methods=["GET", "POST"])
def start_adding_item(item_name):
    """
    Start adding data for this item.

    :param item_name:
    """
    # Reset the session variables.
    session[r.SK_CUR_ITEM] = item_name
    group_name = session.get(r.SK_GROUP_NAME, "")

    # Return basic page if this is a get request!!
    if request.method == "GET":
        return render_template(
            "add_item/start.html",
            item_name=item_name,
            item_url=r.get_item_url(item_name),
            group_name=group_name,
            is_toggle_selected=session.get(r.SK_USE_GROUP_VALUES, True),
            group_categories=r.category_names_to_html_ids(get_group_categories(group_name)),
            # TODO - toggle for testing.
            # show_group=True,
            show_group=should_show_group(group_name))

    # Update group name and reload this page (if applicable).
    if "group-name-btn" in request.form:
        new_group_name = request.form["group-name"]
        update_group(group_name, new_group_name, item_name)
        session[r.SK_GROUP_NAME] = new_group_name
        return redirect(url_for("add.start_adding_item", item_name=item_name))

    if maybe_group_toggle_update_saved(session, request.form):
        return redirect(url_for("add.start_adding_item", item_name=item_name))

    methods = []
    if "breaking" in request.form.keys():
        methods.append("add.breaking")
    if "crafting" in request.form.keys():
        methods.append("add.crafting")
    if "env-changes" in request.form.keys():
        methods.append("add.env_changes")
    session[r.SK_METHOD_LIST] = methods

    create_json_file(item_name)
    write_group_name_to_item_json(item_name, group_name)
    return move_next_category(item_name)


@item_blueprint.route("/")
def start():
    session.clear()
    return redirect(url_for("add.start_adding_item", item_name=get_next_item()))

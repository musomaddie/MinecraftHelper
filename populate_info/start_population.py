from flask import Blueprint, redirect, render_template, request, session, url_for

import populate_info.resources as r
from populate_info.group_utils import update_group, get_group_categories, maybe_group_toggle_update_saved
from populate_info.json_utils import get_next_item

bp = Blueprint("add", __name__)


@bp.route("/add_item/<item_name>", methods=["GET", "POST"])
def start_adding_item(item_name):
    """
    Start adding data for this item.

    :param item_name:
    """
    item_file_name = r.get_item_fn(item_name)
    # Don't save to the JSON file until the end, use session for now.
    session[r.CUR_ITEM_SK] = item_name
    group_name = session.get(r.GROUP_NAME_SK, "")

    # Return basic page if this is a get request!!
    if request.method == "GET":
        return render_template(
            "add_item/start.html",
            item_name=item_name,
            item_url=r.get_item_url(item_name),
            group_name=group_name,
            checked_from_group=get_group_categories("TESTING_GROUP"),
            is_toggle_selected=session.get(r.USE_GROUP_VALUES_SK, True),
            # Temporarily on for testing
            show_group=True)
        # show_group=should_show_group(group_name))

    # Update group name and reload this page (if applicable).
    if "group_name_btn" in request.form:
        new_group_name = request.form["group_name"]
        update_group(group_name, new_group_name, item_name)
        session[r.GROUP_NAME_SK] = new_group_name
        return redirect(url_for("add.start_adding_item", item_name=item_name))

    if maybe_group_toggle_update_saved(request.form):
        return redirect(url_for("add.start_adding_item", item_name=item_name))

    methods = []
    if "breaking" in request.form.keys():
        methods.append("add.breaking")

    # TODO: temp for testing
    return render_template(
        "add_item/start.html",
        item_name=item_name,
        item_url=r.get_item_url(item_name),
        group_name=group_name,
        # js_data={"is_toggled_selected": True},
        # checked_from_group=
        # Temporarily on for testing
        is_toggle_selected=session.get(r.USE_GROUP_VALUES_SK, True),
        show_group=True)


# @bp.route("/add_item/<item_name>", methods=["GET", "POST"])
# def item(item_name):
#     item_file_name = item_name + ".json"
#     item_file_name_full = f"{JSON_DIR}/{item_file_name}"
#     existing_json_data = {}
#     if isfile(join(JSON_DIR, item_file_name)):
#         existing_json_data = get_file_contents(item_file_name_full)
#         _add_to_item_list(item_name)
#     else:
#         existing_json_data["name"] = item_name
#         update_json_file(existing_json_data, item_file_name_full)
#     group_name = get_updated_group_name(get_group(item_name), existing_json_data)
#     save_to_group(group_name, item_name)
#     group_info = ExistingGroupInfo.load_from_session(group_name, item_name)
#     item_url = f"{URL_BLOCK_PAGE_TEMPLATE}{item_name.replace(' ', '%20')}"
#     if request.method == "GET":
#         return render_template(
#             "add_block_start.html",
#             group_name=group_name,
#             show_group=group_info.should_show,
#             toggle_selected=group_info.use_group_items,
#             item_name=item_name,
#             already_checked=group_info.get_obtaining_methods(),
#             block_url=item_url)
#
#     if "update_group" in request.form:
#         remove_from_group(group_name, item_name)
#         new_group_name = request.form["group_name_replacement"]
#         existing_json_data["group"] = new_group_name
#         save_to_group(new_group_name, item_name)
#         update_json_file(existing_json_data, item_file_name_full)
#         ExistingGroupInfo.load_from_session(new_group_name, item_name).update_group_in_session()
#         return redirect(url_for("add.item", item_name=item_name))
#
#     if _check_update_group_toggle(request.form, item_name, group_info):
#         return redirect(url_for("add.item", item_name=item_name))
#
#     methods = []
#     if "breaking" in request.form.keys():
#         methods.append("add.breaking")
#     if "breaking_other" in request.form.keys():
#         methods.append("add.breaking_other")
#     if "crafting" in request.form.keys():
#         methods.append("add.crafting")
#     if "fishing" in request.form.keys():
#         methods.append("add.fishing")
#     if "trading" in request.form.keys():
#         methods.append("add.trading")
#     if "nat_gen" in request.form.keys():
#         methods.append("add.natural_generation")
#     if "nat_biome" in request.form.keys():
#         methods.append("add.natural_generation_biome")
#     if "nat_struct" in request.form.keys():
#         methods.append("add.natural_gen_structure")
#     if "post_gen" in request.form.keys():
#         methods.append("add.post_generation")
#     if "stonecutter" in request.form.keys():
#         methods.append("add.stonecutter")
#     session["remaining_methods"] = methods
#     return move_next_page(item_name)
#
#
# @bp.route("/")
# def start():
#     conn = get_db()
#     cur = conn.cursor()
#     return select_next_item(cur)

@bp.route("/")
def start():
    return redirect(url_for("add.start_adding_item", item_name=get_next_item()))

import json
from os.path import isfile, join

from flask import Blueprint, flash, redirect, render_template, request, session, url_for

from block_adder_flask.db_for_flask import get_db, get_group
from block_adder_flask.get_group_info import (
    ExistingGroupInfo, get_updated_group_name, remove_from_group, save_to_group)
from block_adder_flask.json_utils import (
    append_json_file, get_all_items_json_file,
    get_file_contents, update_json_file)

ITEMS_GROUPS_TN = "item_to_group"
URL_BLOCK_PAGE_TEMPLATE = "https://minecraft.fandom.com/wiki/"
JSON_DIR = "block_adder_flask/item_information"
JSON_ITEM_LIST = "block_adder_flask/item_information/item_list.json"

bp = Blueprint("add", __name__)


def _get_value_if_exists(this_request, key, expected_type=str, default_value=""):
    if expected_type == int:
        return int(this_request.form[key]) if key in this_request.form else default_value
    return this_request.form[key] if key in this_request.form else default_value


def _add_to_item_list(item_name, filename=JSON_ITEM_LIST):
    existing_json = {"items": []}
    with open(filename) as f:
        existing_json = json.load(f)
    if item_name not in existing_json["items"]:
        existing_json["items"].append(item_name)
    update_json_file(existing_json, filename)


def _check_update_group_toggle(
        request_form: dict, item_name: str, group_info: ExistingGroupInfo) -> bool:
    """
    Checks if the toggle for use group has been submitted as part of the form. Returns true if so,
    else false.
    """
    if "existing_group_values" in request_form:
        group_info.use_values_button_clicked("group_checkbox" not in request_form)
        return True
    return False


def select_next_item(cur):
    cur.execute(f"SELECT * FROM {ITEMS_GROUPS_TN}")
    item_name_list = [block["item_name"] for block in cur.fetchall()]
    saved_items = set([f.replace(".json", "") for f in get_all_items_json_file()])
    next_item = [name for name in item_name_list if name not in saved_items][0]
    return redirect(url_for("add.item", item_name=next_item))


def move_next_page(item_name):
    if len(session["remaining_methods"]) == 0:
        return select_next_item(get_db().cursor())
    return redirect(url_for(session["remaining_methods"].pop(0), item_name=item_name))


def continue_work(item_name, repeat_current, current_method_name):
    if repeat_current:
        return redirect(url_for(current_method_name, item_name=item_name))
    return move_next_page(item_name)


@bp.route("/add_breaking/<item_name>", methods=["GET", "POST"])
def breaking(item_name):
    group_info = ExistingGroupInfo.load_from_session(session["group_name"], item_name)
    if request.method == "GET":
        return render_template(
            "add_breaking.html", item_name=item_name,
            show_group=group_info.should_show,
            toggle_selected=group_info.use_group_items,
            existing_info=group_info.get_breaking_info())
    if _check_update_group_toggle(request.form, item_name, group_info):
        return redirect(url_for("breaking", item_name=item_name))
    append_json_file(
        "breaking",
        [("requires tool", request.form["requires_tool"] != "tool_no"),
         ("required tool", request.form["specific_tool"],
          request.form["requires_tool"] == "tool_specific"),
         ("requires silk", request.form["requires_silk"] == "silk_yes"),
         ("fastest tool", request.form["fastest_specific_tool"],
          "fastest_tool" in request.form)],
        f"{JSON_DIR}/{item_name}.json")
    flash(f"Successfully added breaking information for {item_name}")
    return continue_work(item_name, "another" in request.form.keys(), "add.breaking")


@bp.route("/add_breaking_other/<item_name>", methods=["GET", "POST"])
def breaking_other(item_name):
    group_info = ExistingGroupInfo.load_from_session(session["group_name"], item_name)
    if request.method == "GET":
        return render_template(
            "add_breaking_other.html", item_name=item_name,
            show_group=group_info.should_show,
            toggle_selected=group_info.use_group_items,
            existing_info=group_info.get_breaking_other_info(),
        )
    if _check_update_group_toggle(request.form, item_name, group_info):
        return redirect(url_for("breaking_other", item_name=item_name))
    append_json_file(
        "breaking other",
        [("other block name", request.form["other_block"]),
         ("likelihood of dropping", float(_get_value_if_exists(request, "percent_dropping")),
          "percent_dropping" in request.form),
         ("helped with fortune", "fortune" in request.form)],
        f"{JSON_DIR}/{item_name}.json")
    flash(f"Successfully added breaking other information for {item_name}")
    return continue_work(item_name, "another" in request.form.keys(), "add.breaking_other")


@bp.route("/add_crafting/<item_name>", methods=["GET", "POST"])
def crafting(item_name):
    if request.method == "GET":
        return render_template("add_crafting.html", item_name=item_name)
    append_json_file(
        "crafting",
        [("crafting slots", [
            _get_value_if_exists(request, "cs1"),
            _get_value_if_exists(request, "cs2"),
            _get_value_if_exists(request, "cs3"),
            _get_value_if_exists(request, "cs4"),
            _get_value_if_exists(request, "cs5"),
            _get_value_if_exists(request, "cs6"),
            _get_value_if_exists(request, "cs7"),
            _get_value_if_exists(request, "cs8"),
            _get_value_if_exists(request, "cs9")]),
         ("num created", int(request.form["n_created"])),
         ("works with four by four", "works_four" in request.form),
         ("requires exact positioning", "exact_positioning" in request.form)],
        f"{JSON_DIR}/{item_name}.json")
    flash(f"Successfully added crafting information for {item_name}")
    return continue_work(item_name, "another" in request.form.keys(), "add.crafting")


@bp.route("/add_fishing/<item_name>", methods=["GET", "POST"])
def fishing(item_name):
    if request.method == "GET":
        return render_template("add_fishing.html", item_name=item_name)
    append_json_file(
        "fishing", [("treasure type", request.form["item_level"])], f"{JSON_DIR}/{item_name}.json")
    flash(f"Successfully added fishing information for {item_name}")
    return continue_work(item_name, "another" in request.form.keys(), "add.fishing")


@bp.route("/add_natural_generation/<item_name>", methods=["GET", "POST"])
def natural_generation(item_name):
    if request.method == "GET":
        return render_template("add_natural_generation.html", item_name=item_name)
    append_json_file(
        "generated in chests",
        [("structure", request.form["structure"]),
         ("container", _get_value_if_exists(request, "container"), "container" in request.form),
         ("quantity", int(request.form["quantity_fd"])),
         ("chance", float(_get_value_if_exists(request, "chance", default_value=100)),
          "chance" in request.form)],
        f"{JSON_DIR}/{item_name}.json")
    flash(f"Successfully added natural generation in chests information for {item_name}")
    return continue_work(item_name, "another" in request.form.keys(), "add.natural_generation")


@bp.route("/add_natural_biome/<item_name>", methods=["GET", "POST"])
def natural_generation_biome(item_name):
    if request.method == "GET":
        return render_template("add_nat_biome.html")
    append_json_file(
        "generated in biome",
        [("biome name", request.form["biome"])],
        f"{JSON_DIR}/{item_name}.json")
    flash(f"Successfully added generation in biome information for {item_name}")
    return continue_work(
        item_name, "another" in request.form.keys(), "add.natural_generation_biome")


@bp.route("/add_natural_gen_structure/<item_name>", methods=["GET", "POST"])
def natural_gen_structure(item_name):
    if request.method == "GET":
        return render_template("add_nat_structure.html")
    append_json_file(
        "generated as part of structure",
        [("structure name", request.form["structure_name"])],
        f"{JSON_DIR}/{item_name}.json")
    flash(f"Successfully added generation as part of structure information for {item_name}")
    return continue_work(item_name, "another" in request.form.keys(), "add.natural_gen_structure")


@bp.route("/add_trading/<item_name>", methods=["GET", "POST"])
def trading(item_name):
    if request.method == "GET":
        return render_template("add_trading.html", item_name=item_name)
    append_json_file(
        "trading",
        [("villager type", request.form["villager_type"]),
         ("villager level", _get_value_if_exists(request, "villager_level"),
          "villager_level" in request.form),
         ("emerald price", int(request.form["emerald_price"])),
         ("other item required", _get_value_if_exists(request, "other_item"),
          "other_item" in request.form)],
        f"{JSON_DIR}/{item_name}.json"
    )
    flash(f"Successfully added trading information for {item_name}")
    return continue_work(item_name, "another" in request.form.keys(), "add.trading")


@bp.route("/add_post_generation/<item_name>", methods=["GET", "POST"])
def post_generation(item_name):
    if request.method == "GET":
        return render_template("add_post_generation.html", item_name=item_name)
    append_json_file(
        "post generation",
        [("part of", _get_value_if_exists(request, "part_of"), "part_of" in request.form),
         ("generated from", _get_value_if_exists(request, "generated_from"),
          "generated_from" in request.form)],
        f"{JSON_DIR}/{item_name}.json")
    flash(f"Successfully added post generation information for {item_name}")
    return continue_work(item_name, "another" in request.form.keys(), "add.post_generation")


@bp.route("/add_stonecutter/<item_name>", methods=["GET", "POST"])
def stonecutter(item_name):
    if request.method == "GET":
        return render_template("add_stonecutter.html", item_name=item_name)
    append_json_file(
        "stonecutter",
        [("block required", request.form["other_block"]),
         ("quantity made", int(request.form["quantity"]))],
        f"{JSON_DIR}/{item_name}.json")
    flash(f"Successfully added stonecutter information for {item_name}")
    return continue_work(item_name, "another" in request.form.keys(), "add.stonecutter")


@bp.route("/add_item/<item_name>", methods=["GET", "POST"])
def item(item_name):
    item_file_name = item_name + ".json"
    item_file_name_full = f"{JSON_DIR}/{item_file_name}"
    existing_json_data = {}
    if isfile(join(JSON_DIR, item_file_name)):
        existing_json_data = get_file_contents(item_file_name_full)
        _add_to_item_list(item_name)
    else:
        existing_json_data["name"] = item_name
        update_json_file(existing_json_data, item_file_name_full)
    group_name = get_updated_group_name(get_group(item_name), existing_json_data)
    save_to_group(group_name, item_name)
    group_info = ExistingGroupInfo.load_from_session(group_name, item_name)
    item_url = f"{URL_BLOCK_PAGE_TEMPLATE}{item_name.replace(' ', '%20')}"
    if request.method == "GET":
        return render_template(
            "add_block_start.html",
            group_name=group_name,
            show_group=group_info.should_show,
            toggle_selected=group_info.use_group_items,
            item_name=item_name,
            already_checked=group_info.get_obtaining_methods(),
            block_url=item_url)

    if "update_group" in request.form:
        remove_from_group(group_name, item_name)
        new_group_name = request.form["group_name_replacement"]
        existing_json_data["group"] = new_group_name
        save_to_group(new_group_name, item_name)
        update_json_file(existing_json_data, item_file_name_full)
        ExistingGroupInfo.load_from_session(new_group_name, item_name).update_group_in_session()
        return redirect(url_for("add.item", item_name=item_name))

    if _check_update_group_toggle(request.form, item_name, group_info):
        return redirect(url_for("add.item", item_name=item_name))

    methods = []
    if "breaking" in request.form.keys():
        methods.append("add.breaking")
    if "breaking_other" in request.form.keys():
        methods.append("add.breaking_other")
    if "crafting" in request.form.keys():
        methods.append("add.crafting")
    if "fishing" in request.form.keys():
        methods.append("add.fishing")
    if "trading" in request.form.keys():
        methods.append("add.trading")
    if "nat_gen" in request.form.keys():
        methods.append("add.natural_generation")
    if "nat_biome" in request.form.keys():
        methods.append("add.natural_generation_biome")
    if "nat_struct" in request.form.keys():
        methods.append("add.natural_gen_structure")
    if "post_gen" in request.form.keys():
        methods.append("add.post_generation")
    if "stonecutter" in request.form.keys():
        methods.append("add.stonecutter")
    session["remaining_methods"] = methods
    return move_next_page(item_name)


@bp.route("/")
def start():
    conn = get_db()
    cur = conn.cursor()
    return select_next_item(cur)

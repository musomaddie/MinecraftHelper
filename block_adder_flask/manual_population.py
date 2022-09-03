import ast
import json
import os
from os.path import isfile, join

from flask import Blueprint, flash, redirect, render_template, request, url_for

from block_adder_flask.db_for_flask import (
    get_db,
    get_group)

ITEMS_GROUPS_TN = "item_to_group"
URL_BLOCK_PAGE_TEMPLATE = "https://minecraft.fandom.com/wiki/"
JSON_DIR = "block_adder_flask/item_information"
JSON_ITEM_LIST = "block_adder_flask/item_information/item_list.json"

bp = Blueprint("add", __name__)


def _get_value_if_exists(this_request, key, expected_type=str, default_value=""):
    if expected_type == int:
        return int(this_request.form[key]) if key in this_request.form else default_value
    return this_request.form[key] if key in this_request.form else default_value


def _update_json_file(value: dict, filename: str):
    with open(filename, "w") as f:
        json.dump(value, f)


def _append_json_file(future_key: str, value: dict, filename: str):
    current_content = _get_file_contents(filename)
    if future_key in current_content:
        if type(current_content[future_key]) != list:
            current_content[future_key] = [current_content[future_key]]
        current_content[future_key].append(value)
    else:
        current_content[future_key] = value
    _update_json_file(current_content, filename)


def _get_all_items_json_file(filename=JSON_ITEM_LIST):
    with open(filename) as f:
        return json.load(f)["items"]


def _get_file_contents(filename: str):
    with open(filename) as f:
        return json.load(f)


def _add_to_item_list(item_name, filename=JSON_ITEM_LIST):
    existing_json = {"items": []}
    with open(filename) as f:
        existing_json = json.load(f)
    if item_name not in existing_json:
        existing_json["items"].append(item_name)
    _update_json_file(existing_json, filename)


def _get_updated_group_name(from_db: str, json_data: dict) -> str:
    if "group" in json_data:
        return json_data["group"]
    return from_db


def _save_to_group(group_name, item_name):
    if group_name == "":
        return
    group_dir = f"{JSON_DIR}/groups"
    group_fn_full = f"{group_dir}/{group_name}.json"
    if isfile(join(group_dir, group_name)):
        existing_group_items = _get_file_contents(group_fn_full)
        if item_name in existing_group_items["items"]:
            return
        existing_group_items["items"].append(item_name)
        _update_json_file(existing_group_items, group_fn_full)
    else:
        group_items = {"group name": group_name, "items": [item_name]}
        _update_json_file(group_items, group_fn_full)


def _remove_from_group(group_name, item_name):
    if group_name == "":
        return
    group_fn_full = f"{JSON_DIR}/groups/{group_name}.json"
    existing_group_info = _get_file_contents(group_fn_full)
    existing_group_info["items"].remove(item_name)
    if len(existing_group_info["items"]) == 0:
        os.remove(group_fn_full)
    else:
        _update_json_file(existing_group_info, group_fn_full)


def select_next_item(cur):
    cur.execute(f"SELECT * FROM {ITEMS_GROUPS_TN}")
    item_name_list = [block["item_name"] for block in cur.fetchall()]
    saved_items = set([f.replace(".json", "") for f in _get_all_items_json_file()])
    next_item = [name for name in item_name_list if name not in saved_items][0]
    return redirect(url_for("add.item", item_name=next_item))


def move_next_page(item_name, remaining_items):
    # Get the first item
    if type(remaining_items) == str:
        remaining_items = ast.literal_eval(remaining_items)
    if len(remaining_items) == 0:
        return select_next_item(get_db().cursor())
    next_method = remaining_items.pop(0)
    return redirect(url_for(next_method, item_name=item_name, remaining_items=remaining_items))


@bp.route("/add_breaking/<item_name>/<remaining_items>", methods=["GET", "POST"])
def breaking(item_name, remaining_items):
    if request.method == "GET":
        return render_template("add_breaking.html", item_name=item_name)
    _append_json_file(
        "breaking",
        {"requires tool": request.form["requires_tool"] == "tool_yes",
         "requires silk": request.form["requires_silk"] == "silk_yes",
         "fastest tool": _get_value_if_exists(request, "fastest_tool")},
        f"{JSON_DIR}/{item_name}.json")
    flash(f"Successfully added breaking information for {item_name}")
    if "next" in request.form.keys():
        return move_next_page(item_name, remaining_items)
    return redirect(
        url_for("add.breaking", item_name=item_name, remaining_items=remaining_items))


@bp.route("/add_crafting/<item_name>/<remaining_items>", methods=["GET", "POST"])
def crafting(item_name, remaining_items):
    if request.method == "GET":
        return render_template("add_crafting.html", item_name=item_name)
    _append_json_file(
        "crafting", {
            "crafting slots": [
                _get_value_if_exists(request, "cs1"),
                _get_value_if_exists(request, "cs2"),
                _get_value_if_exists(request, "cs3"),
                _get_value_if_exists(request, "cs4"),
                _get_value_if_exists(request, "cs5"),
                _get_value_if_exists(request, "cs6"),
                _get_value_if_exists(request, "cs7"),
                _get_value_if_exists(request, "cs8"),
                _get_value_if_exists(request, "cs9"),
            ],
            "num created": int(request.form["n_created"]),
            "works with four by four": "works_four" in request.form,
            "requires exact positioning": "exact_positioning" in request.form
        },
        f"{JSON_DIR}/{item_name}.json"
    )
    flash(f"Successfully added crafting information for {item_name}")
    if "next" in request.form.keys():
        return move_next_page(item_name, remaining_items)
    return redirect(
        url_for("add.crafting", item_name=item_name, remaining_items=remaining_items))


@bp.route("/add_fishing/<item_name>/<remaining_items>", methods=["GET", "POST"])
def fishing(item_name, remaining_items):
    if request.method == "GET":
        return render_template("add_fishing.html", item_name=item_name)
    _append_json_file(
        "fishing", {"treasure type": request.form["item_level"]}, f"{JSON_DIR}/{item_name}.json")
    flash(f"Successfully added fishing information for {item_name}")
    return move_next_page(item_name, remaining_items)


@bp.route("/add_natural_generation/<item_name>/<remaining_items>", methods=["GET", "POST"])
def natural_generation(item_name, remaining_items):
    if request.method == "GET":
        return render_template("add_natural_generation.html", item_name=item_name)
    _append_json_file(
        "generated in chests",
        {"structure": request.form["structure"],
         "container": _get_value_if_exists(request, "container"),
         "quantity": int(request.form["quantity_fd"]),
         "chance": _get_value_if_exists(request, "chance", expected_type=int, default_value=100)
         },
        f"{JSON_DIR}/{item_name}.json")
    flash(f"Successfully added natural generation in chests information for {item_name}")
    if "next" in request.form.keys():
        return move_next_page(item_name, remaining_items)
    return redirect(
        url_for(
            "add.natural_generation",
            item_name=item_name,
            remaining_items=remaining_items))


@bp.route("/add_natural_biome/<item_name>/<remaining_items>", methods=["GET", "POST"])
def natural_generation_biome(item_name, remaining_items):
    if request.method == "GET":
        return render_template("add_nat_biome.html")
    _append_json_file(
        "generated in biome", {"biome name": request.form["biome"]}, f"{JSON_DIR}/{item_name}.json")
    flash(f"Successfully added generation in biome information for {item_name}")
    return move_next_page(item_name, remaining_items)


@bp.route("/add_natural_gen_structure/<item_name>/<remaining_items>", methods=["GET", "POST"])
def natural_gen_structure(item_name, remaining_items):
    if request.method == "GET":
        return render_template("add_nat_structure.html")
    _append_json_file(
        "generated as part of structure",
        {"structure name": request.form["structure_name"]}, f"{JSON_DIR}/{item_name}.json")
    flash(f"Successfully added generation as part of structure information for {item_name}")
    if "next" in request.form.keys():
        return move_next_page(item_name, remaining_items)
    return redirect(
        url_for(
            "add.natural_gen_structure", item_name=item_name, remaining_items=remaining_items))


@bp.route("/add_trading/<item_name>/<remaining_items>", methods=["GET", "POST"])
def trading(item_name, remaining_items):
    if request.method == "GET":
        return render_template("add_trading.html", item_name=item_name)
    _append_json_file(
        "trading",
        {"villager type": request.form["villager_type"],
         "villager level": _get_value_if_exists(request, "villager_level"),
         "emerald price": int(request.form["emerald_price"]),
         "other item required": _get_value_if_exists(request, "other_item")},
        f"{JSON_DIR}/{item_name}.json"
    )
    flash(f"Successfully added trading information for {item_name}")
    return move_next_page(item_name, remaining_items)


@bp.route("/add_post_generation/<item_name>/<remaining_items>", methods=["GET", "POST"])
def post_generation(item_name, remaining_items):
    if request.method == "GET":
        return render_template("add_post_generation.html", item_name=item_name)
    _append_json_file(
        "post generation",
        {"part of": _get_value_if_exists(request, "part_of"),
         "generated from": _get_value_if_exists(request, "generated_from")},
        f"{JSON_DIR}/{item_name}.json")
    flash(f"Successfully added post generation information for {item_name}")
    return move_next_page(item_name, remaining_items)


@bp.route("/add_item/<item_name>", methods=["GET", "POST"])
def item(item_name):
    item_file_name = item_name + ".json"
    item_file_name_full = f"{JSON_DIR}/{item_file_name}"
    existing_json_data = {}
    # TODO: handle groups more sensibly - so I can find what is in each group without having to
    #  open every file.
    if isfile(join(JSON_DIR, item_file_name)):
        existing_json_data = _get_file_contents(item_file_name_full)
        _add_to_item_list(item_name)
    else:
        existing_json_data["name"] = item_name
        _update_json_file(existing_json_data, item_file_name_full)
    group_name = _get_updated_group_name(get_group(item_name), existing_json_data)
    _save_to_group(group_name, item_name)
    if request.method == "GET":
        return render_template(
            "add_block_start.html",
            group_name=group_name,
            item_name=item_name,
            block_url=f"{URL_BLOCK_PAGE_TEMPLATE}{item_name.replace(' ', '%20')}")

    if "update_group" in request.form:
        _remove_from_group(
            existing_json_data["group"] if "group" in existing_json_data else "", item_name)
        existing_json_data["group"] = request.form["group_name_replacement"]
        _update_json_file(existing_json_data, item_file_name_full)
        return redirect(url_for("add.item", item_name=item_name))

    methods = []
    if "breaking" in request.form.keys():
        methods.append("add.breaking")
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
    return move_next_page(item_name, methods)


@bp.route("/")
def start():
    conn = get_db()
    cur = conn.cursor()
    return select_next_item(cur)

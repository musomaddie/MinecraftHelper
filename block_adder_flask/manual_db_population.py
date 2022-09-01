import ast
import json
from os.path import isfile, join

from flask import Blueprint, flash, redirect, render_template, request, url_for

from block_adder_flask.db_for_flask import (
    add_nat_structure_to_db, add_trading_to_db, get_db,
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


def select_next_item(cur):
    cur.execute(f"SELECT * FROM {ITEMS_GROUPS_TN}")
    item_name_list = [block["item_name"] for block in cur.fetchall()]
    saved_items = set([f.replace(".json", "") for f in _get_all_items_json_file()])
    next_item = [name for name in item_name_list if name not in saved_items][0]
    return redirect(url_for("add.item", next_item))


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
    flash(f"Successfully added {item_name} to the breaking table")
    return move_next_page(item_name, remaining_items)


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
    flash(f"Successfully added {item_name} to crafting")
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
    flash(f"Successfully added {item_name} to fishing")
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
    flash(f"Successfully added {item_name} to natural generation table")
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
    flash(f"Successfully added {item_name} to biome")
    return move_next_page(item_name, remaining_items)


@bp.route("/add_natural_gen_structure/<item_name>/<remaining_items>", methods=["GET", "POST"])
def natural_gen_structure(item_name, remaining_items):
    if request.method == "GET":
        return render_template("add_nat_structure.html")
    add_nat_structure_to_db(
        get_db(), item_name, request.form["structure_name"])
    # TODO: add rooms as an optional
    flash(f"Successfully added {item_name} to natural structure generation")
    if "next" in request.form.keys():
        return move_next_page(item_name, remaining_items)
    return redirect(
        url_for(
            "add.natural_gen_structure", item_name=item_name, remaining_items=remaining_items))


@bp.route("/add_trading/<item_name>/<remaining_items>", methods=["GET", "POST"])
def trading(item_name, remaining_items):
    if request.method == "GET":
        return render_template("add_trading.html", item_name=item_name)
    add_trading_to_db(
        get_db(), item_name,
        request.form["villager_type"], _get_value_if_exists(request, "villager_level"),
        int(request.form["emerald_price"]), _get_value_if_exists(request, "other_item"))
    flash(f"Successfully added {item_name} to trading table.")
    return move_next_page(item_name, remaining_items)


@bp.route("/add_item/<item_name>", methods=["GET", "POST"])
def item(item_name):
    item_file_name = item_name + ".json"
    item_file_name_full = f"{JSON_DIR}/{item_file_name}"
    existing_json_data = {}
    if isfile(join(JSON_DIR, item_file_name)):
        # TODO: rewrite to use reading helper
        existing_json_data = _get_file_contents(item_file_name_full)
        _add_to_item_list(item_name)
    else:
        existing_json_data["name"] = item_name
        _update_json_file(existing_json_data, item_file_name_full)
    group_name = _get_updated_group_name(get_group(item_name), existing_json_data)
    if request.method == "GET":
        return render_template(
            "add_block_start.html",
            group_name=group_name,
            item_name=item_name,
            block_url=f"{URL_BLOCK_PAGE_TEMPLATE}{item_name.replace(' ', '%20')}")

    if "update_group" in request.form:
        existing_json_data["group"] = request.form["group_name_replacement"]
        _update_json_file(existing_json_data, item_file_name_full)
        return render_template(
            "add_block_start.html",
            group_name=group_name,
            item_name=item_name,
            block_url=f"{URL_BLOCK_PAGE_TEMPLATE}{item_name.replace(' ', '%20')}")

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
    return move_next_page(item_name, methods)


# @bp.route("/start_new")
# def start_new():
#     reset_entire_db()
#     return "I am starting new"


# @bp.route("/new_table/<table_name>")
# def new_table(table_name):
#     conn = get_db()
#     reset_table(conn, conn.cursor(), table_name)
#     return f"Added {table_name} to database"


@bp.route("/")
def start():
    conn = get_db()
    cur = conn.cursor()
    return select_next_item(cur)

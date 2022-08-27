import ast

from flask import Blueprint, flash, redirect, render_template, request, url_for

from block_adder_flask.db_for_flask import (
    add_breaking_to_db, add_fishing_to_db, add_nat_biome_to_db, add_natural_gen_to_db,
    add_trading_to_db, get_db, reset_entire_db)

ITEMS_GROUPS_TN = "item_to_group"
URL_BLOCK_PAGE_TEMPLATE = "https://minecraft.fandom.com/wiki/"

bp = Blueprint("add", __name__)


def select_next_item(cur):
    cur.execute(f"SELECT * FROM {ITEMS_GROUPS_TN}")
    item_name_list = [block["item_name"] for block in cur.fetchall()]
    cur.execute(f"SELECT item_name FROM item_obtaining_method")
    saved_items = set([row["item_name"] for row in cur.fetchall()])
    item_name_list = [name for name in item_name_list if name not in saved_items]
    return redirect(url_for("add_block", item_name=item_name_list[0]))


def move_next_page(item_name, remaining_items):
    # Get the first item
    if type(remaining_items) == str:
        remaining_items = ast.literal_eval(remaining_items)
    if len(remaining_items) == 0:
        return select_next_item(get_db().cursor())
    next_method = remaining_items.pop(0)
    return redirect(url_for(next_method, item_name=item_name, remaining_items=remaining_items))


@bp.route("/add_breaking/<item_name>/<remaining_items>", methods=["GET", "POST"])
def add_breaking(item_name, remaining_items):
    if request.method == "GET":
        return render_template("add_breaking.html", item_name=item_name)
    requires_tool = request.form["requires_tool"]
    requires_silk = request.form["requires_silk"]
    fastest_tool = request.form["fastest_tool"] if "fastest_tool" in request.form else ""
    add_breaking_to_db(get_db(), item_name, requires_tool, requires_silk, fastest_tool)
    flash(f"Successfully added {item_name} to the breaking table")
    return move_next_page(item_name, remaining_items)


@bp.route("/add_fishing/<item_name>/<remaining_items>", methods=["GET", "POST"])
def add_fishing(item_name, remaining_items):
    if request.method == "GET":
        return render_template("add_fishing.html", item_name=item_name)
    item_lvl = request.form["item_level"]
    add_fishing_to_db(get_db(), item_name, item_lvl)
    flash(f"Successfully added {item_name} to fishing")
    return move_next_page(item_name, remaining_items)


@bp.route("/add_natural_generation/<item_name>/<remaining_items>", methods=["GET", "POST"])
def add_natural_generation(item_name, remaining_items):
    if request.method == "GET":
        return render_template("add_natural_generation.html", item_name=item_name)
    structure = request.form["structure"]
    container = request.form["container"]
    quant = int(request.form["quantity_fd"])
    ch = int(request.form["chance"])
    add_natural_gen_to_db(get_db(), item_name, structure, container, quant, ch)
    flash(f"Successfully added {item_name} to natural generation table")
    if "next" in request.form.keys():
        return move_next_page(item_name, remaining_items)
    return redirect(
        url_for(
            "add_natural_generation",
            item_name=item_name,
            remaining_items=remaining_items))


@bp.route("/add_natural_biome/<item_name>/<remaining_items>", methods=["GET", "POST"])
def add_natural_generation_biome(item_name, remaining_items):
    if request.method == "GET":
        return render_template("add_nat_biome.html")
    biome = request.form["biome"]
    add_nat_biome_to_db(get_db(), item_name, biome)
    flash(f"Successfully added {item_name} to biome")
    return move_next_page(item_name, remaining_items)


@bp.route("/add_trading/<item_name>/<remaining_items>", methods=["GET", "POST"])
def add_trading(item_name, remaining_items):
    if request.method == "GET":
        return render_template("add_trading.html", item_name=item_name)
    villager_type = request.form["villager_type"]
    emerald_price = int(request.form["emerald_price"])
    village_level = request.form["villager_level"] if "villager_level" in request.form else ""
    other_item = request.form["other_item"] if "other_item" in request.form else ""
    add_trading_to_db(get_db(), item_name, villager_type, village_level, emerald_price, other_item)
    flash(f"Successfully added {item_name} to trading table.")
    return move_next_page(item_name, remaining_items)


@bp.route("/add_block/<item_name>", methods=["GET", "POST"])
def add_block(item_name):
    if request.method == "GET":
        return render_template(
            "add_block_start.html",
            item_name=item_name,
            block_url=f"{URL_BLOCK_PAGE_TEMPLATE}{item_name.replace(' ', '%20')}")
    methods = []
    if "trading" in request.form.keys():
        methods.append("add_trading")
    if "nat_gen" in request.form.keys():
        methods.append("add_natural_generation")
    if "breaking" in request.form.keys():
        methods.append("add_breaking")
    if "fishing" in request.form.keys():
        methods.append("add_fishing")
    if "nat_biome" in request.form.keys():
        methods.append("add_natural_biome")
    return move_next_page(item_name, methods)


@bp.route("/start_new")
def start_new():
    reset_entire_db()
    return "I am starting new"


@bp.route("/")
def start():
    # conn = get_db()
    # cur = conn.cursor()
    # print("I have started")
    # return select_next_block(cur)
    return "Hello world I am starting!"

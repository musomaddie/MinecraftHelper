import ast

from flask import Blueprint, flash, redirect, render_template, request, url_for

from block_adder_flask.db_for_flask import (
    add_breaking_to_db, add_crafting_recipe_to_db, add_fishing_to_db, add_nat_biome_to_db,
    add_natural_gen_to_db,
    add_trading_to_db, get_db, reset_entire_db, reset_table)

ITEMS_GROUPS_TN = "item_to_group"
URL_BLOCK_PAGE_TEMPLATE = "https://minecraft.fandom.com/wiki/"

bp = Blueprint("add", __name__)


def _get_value_if_exists(this_request, key):
    return this_request.form[key] if key in this_request.form else ""


def select_next_item(cur):
    cur.execute(f"SELECT * FROM {ITEMS_GROUPS_TN}")
    item_name_list = [block["item_name"] for block in cur.fetchall()]
    cur.execute(f"SELECT item_name FROM item_obtaining_method")
    saved_items = set([row["item_name"] for row in cur.fetchall()])
    item_name_list = [name for name in item_name_list if name not in saved_items]
    return redirect(url_for("add.item", item_name=item_name_list[0]))


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
    requires_tool = request.form["requires_tool"]
    requires_silk = request.form["requires_silk"]
    fastest_tool = _get_value_if_exists(request, "fastest_tool")
    add_breaking_to_db(
        get_db(), item_name,
        request.form["requires_tool"],
        request.form["requires_silk"],
        _get_value_if_exists(request, "fastest_tool"))
    flash(f"Successfully added {item_name} to the breaking table")
    return move_next_page(item_name, remaining_items)


@bp.route("/add_crafting/<item_name>/<remaining_items>", methods=["GET", "POST"])
def crafting(item_name, remaining_items):
    if request.method == "GET":
        return render_template("add_crafting.html", item_name=item_name)
    cs1 = _get_value_if_exists(request, "cs1")
    cs2 = _get_value_if_exists(request, "cs2")
    cs3 = _get_value_if_exists(request, "cs3")
    cs4 = _get_value_if_exists(request, "cs4")
    cs5 = _get_value_if_exists(request, "cs5")
    cs6 = _get_value_if_exists(request, "cs6")
    cs7 = _get_value_if_exists(request, "cs7")
    cs8 = _get_value_if_exists(request, "cs8")
    cs9 = _get_value_if_exists(request, "cs9")
    num_created = int(request.form["n_created"])
    works_four = _get_value_if_exists(request, "works_four")
    exact_positioning = _get_value_if_exists(request, "exact_positioning")
    add_crafting_recipe_to_db(
        get_db(),
        item_name,
        [_get_value_if_exists(request, "cs1"), _get_value_if_exists(request, "cs2"),
         _get_value_if_exists(request, "cs3"), _get_value_if_exists(request, "cs4"),
         _get_value_if_exists(request, "cs5"), _get_value_if_exists(request, "cs6"),
         _get_value_if_exists(request, "cs7"), _get_value_if_exists(request, "cs8"),
         _get_value_if_exists(request, "cs9")],
        int(request.form["n_created"]),
        _get_value_if_exists(request, "works_four"),
        _get_value_if_exists(request, "exact_positioning")
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
    add_fishing_to_db(get_db(), item_name, request.form["item_level"])
    flash(f"Successfully added {item_name} to fishing")
    return move_next_page(item_name, remaining_items)


@bp.route("/add_natural_generation/<item_name>/<remaining_items>", methods=["GET", "POST"])
def natural_generation(item_name, remaining_items):
    if request.method == "GET":
        return render_template("add_natural_generation.html", item_name=item_name)
    structure = request.form["structure"]
    container = request.form["container"]
    quant = int(request.form["quantity_fd"])
    ch = int(request.form["chance"])
    add_natural_gen_to_db(
        get_db(), item_name,
        request.form["structure"],
        request.form["container"],
        int(request.form["quantity_fd"]),
        int(request.form["chance"]))
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
    add_nat_biome_to_db(get_db(), item_name, request.form["biome"])
    flash(f"Successfully added {item_name} to biome")
    return move_next_page(item_name, remaining_items)


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
    if request.method == "GET":
        return render_template(
            "add_block_start.html",
            item_name=item_name,
            block_url=f"{URL_BLOCK_PAGE_TEMPLATE}{item_name.replace(' ', '%20')}")
    methods = []
    if "trading" in request.form.keys():
        methods.append("add.trading")
    if "nat_gen" in request.form.keys():
        methods.append("add.natural_generation")
    if "breaking" in request.form.keys():
        methods.append("add.breaking")
    if "fishing" in request.form.keys():
        methods.append("add.fishing")
    if "nat_biome" in request.form.keys():
        methods.append("add.natural_biome")
    if "crafting" in request.form.keys():
        methods.append("add.crafting")
    return move_next_page(item_name, methods)


@bp.route("/start_new")
def start_new():
    reset_entire_db()
    return "I am starting new"


@bp.route("/new_table/<table_name>")
def new_table(table_name):
    conn = get_db()
    reset_table(conn, conn.cursor(), table_name)
    return f"Added {table_name} to database"


@bp.route("/")
def start():
    conn = get_db()
    cur = conn.cursor()
    return select_next_item(cur)

import ast

from flask import Flask, flash, redirect, render_template, request, url_for

from db_for_flask import add_natural_gen_to_db, get_db

app = Flask(__name__)
app.secret_key = "SECRET KEY EXAMPLE"
ITEMS_GROUPS_TN = "items_and_groups"
URL_BLOCK_PAGE_TEMPLATE = "https://minecraft.fandom.com/wiki/"


def select_next_block(cur):
    cur.execute(f"SELECT * FROM {ITEMS_GROUPS_TN}")
    block_list = [{"name": r[0], "is_group": r[1] == "True", "part_of_group": r[2] == "True"}
                  for r in cur.fetchall()]
    block_name_list = [block["name"] for block in block_list]
    cur.execute(f"SELECT item_name FROM item_obtaining_method")
    saved_items = set([row[0] for row in cur.fetchall()])
    block_name_list = [name for name in block_name_list if name not in saved_items]
    return redirect(url_for("add_block", block_name=block_name_list[0]))


def move_next_page(block_name, remaining_items):
    # Get the first item
    if type(remaining_items) == str:
        remaining_items = ast.literal_eval(remaining_items)
    next_method = remaining_items.pop(0)
    return redirect(url_for(next_method, block_name=block_name, remaining_items=remaining_items))


@app.route("/add_natural_generation/<block_name>/<remaining_items>", methods=["GET", "POST"])
def add_natural_generation(block_name, remaining_items):
    if request.method == "GET":
        return render_template("add_natural_generation.html", block_name=block_name)
    structure = request.form["structure"]
    container = request.form["container"]
    quant = request.form["quantity_fd"]
    ch = request.form["chance"]
    add_natural_gen_to_db(get_db(), block_name, structure, container, quant, ch)
    flash(f"Successfully added {block_name} to natural generation table")
    if "next" in request.form.keys():
        return move_next_page(block_name, remaining_items)
    return redirect(
        url_for(
            "add_natural_generation",
            block_name=block_name,
            remaining_items=remaining_items))


@app.route("/add_trading/<block_name>/<remaining_items>", methods=["GET", "POST"])
def add_trading(block_name, remaining_items):
    if request.method == "GET":
        return render_template("add_trading.html", block_name=block_name)
    villager_type = request.form["villager_type"]
    emerald_price = request.form["emerald_price"]
    village_level = request.form["villager_level"]  # "" if not present
    other_item = request.form["other_item"]
    # add_trading_to_db(get_db(), villager_type, village_level, emerald_price, other_item)
    flash(f"Successfully added {block_name} to trading table.")
    return move_next_page(block_name, remaining_items)


@app.route("/add_block/<block_name>", methods=["GET", "POST"])
def add_block(block_name):
    if request.method == "GET":
        return render_template(
            "add_block_start.html",
            block_name=block_name,
            block_url=f"{URL_BLOCK_PAGE_TEMPLATE}{block_name.replace(' ', '%20')}")
    methods = []
    # if "trading" in request.form.keys():
    #     methods.append("add_trading")
    if "nat_gen" in request.form.keys():
        methods.append("add_natural_generation")
    # Get the correct method list for each step.
    return move_next_page(block_name, methods)


@app.route("/")
def start():
    conn = get_db()
    cur = conn.cursor()
    return select_next_block(cur)

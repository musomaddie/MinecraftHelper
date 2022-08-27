import sqlite3
from sqlite3 import PARSE_DECLTYPES, Row

import click
from flask import current_app, g

DB_S = "block_adder_flask/db/scripts/schema/"
DB_INSERT_FN = "block_adder_flask/db/scripts/insert_into/"

BREAKING_TN = "item_breaking"
CRAFTING_TN = "crafting_recipe"
FISHING_TN = "item_fishing"
NAT_BIOME_TN = "item_generation_biome"
NAT_GEN_TN = "item_natural_generation"
OBTAINING_TN = "item_obtaining_method"
TRADING_TN = "item_trading"

ALL_TABLE_NAMES = [
    BREAKING_TN,
    CRAFTING_TN,
    FISHING_TN,
    NAT_BIOME_TN,
    NAT_GEN_TN,
    OBTAINING_TN,
    TRADING_TN
]


def get_db():
    if "db" not in g:
        # print("Connecting for the first time")
        g.db = sqlite3.connect(
            current_app.config["DATABASE"],
            detect_types=PARSE_DECLTYPES
        )
        g.db.row_factory = Row
        sqlite3.register_adapter(bool, int)
        sqlite3.register_converter("BOOLEAN", lambda v: bool(int(v)))

    return g.db


def close_db(e=None):
    db = g.pop("db", None)
    if db is not None:
        db.close()


def add_to_obtaining_table(
        conn, cur, item_name, method_name, id_title, table_name, name_col_identifier="item_name"):
    cur.execute(
        f'''SELECT {id_title} FROM {table_name} WHERE {name_col_identifier} = "{item_name}"'''
    )
    ids = [row[0] for row in cur.fetchall()]
    for i in ids:
        with open(f"{DB_INSERT_FN}{OBTAINING_TN}.sql") as f:
            conn.execute(f.read(), [item_name, method_name, i])
    conn.commit()


def add_breaking_to_db(conn, item_name, r_tool_s, r_silk_s, f_tool):
    r_tool = r_tool_s == "tool_yes"
    r_silk = r_silk_s == "silk_yes"
    if f_tool == "":
        with open(f"{DB_INSERT_FN}{BREAKING_TN}_without_fastest.sql") as f:
            conn.execute(f.read(), [item_name, r_tool, r_silk])
    else:
        with open(f"{DB_INSERT_FN}{BREAKING_TN}_all_values.sql") as f:
            conn.execute(f.read(), [item_name, r_tool, r_silk, f_tool])
    conn.commit()
    add_to_obtaining_table(conn, conn.cursor(), item_name, "breaking", "breaking_id", BREAKING_TN)


def add_crafting_recipe_to_db(
        conn,
        item_name,
        crafting_slot_list,
        number_created,
        works_four_by_four,
        requires_exact_positioning):
    number_items = sum([1 for item in crafting_slot_list if item != ""])
    item_values = [item for item in crafting_slot_list if item != ""]
    item_indices = [i + 1 for i, item in enumerate(crafting_slot_list) if item != ""]
    cur = conn.cursor()
    if number_items == 1:
        with open(f"{DB_INSERT_FN}{CRAFTING_TN}_one_item.sql") as f:
            conn.execute(f.read(), [item_name, item_values[0], number_created])
    else:
        insert_into_string = ", ".join([f"crafting_slot_{idx}" for idx in item_indices])
        num_question_marks = 4 + number_items
        question_mark_string = ", ".join(["?" for _ in range(num_question_marks)])
        passed_values = [item_name]
        passed_values.extend([v for v in item_values])
        passed_values.extend([number_created, works_four_by_four, requires_exact_positioning])
        cur.execute(
            f'''INSERT INTO crafting_recipe (
                    item_created, {insert_into_string}, number_created, 
                    works_four_by_four, requires_exact_positioning)
                VALUES ({question_mark_string})''',
            passed_values)
    conn.commit()
    add_to_obtaining_table(
        conn, conn.cursor(), item_name, "crafting", "recipe_id", CRAFTING_TN,
        name_col_identifier="item_created")


def add_fishing_to_db(conn, item_name, item_lvl):
    with open(f"{DB_INSERT_FN}{FISHING_TN}.sql") as f:
        conn.execute(f.read(), [item_name, item_lvl])
    conn.commit()
    add_to_obtaining_table(conn, conn.cursor(), item_name, "fishing", "fishing_id", FISHING_TN)


def add_nat_biome_to_db(conn, item_name, biome):
    with open(f"{DB_INSERT_FN}{NAT_BIOME_TN}.sql") as f:
        conn.execute(f.read(), [item_name, biome])
    conn.commit()
    add_to_obtaining_table(conn, conn.cursor(), item_name, "biome", "generation_id", NAT_BIOME_TN)


def add_natural_gen_to_db(conn, item_name, struct, cont, quant, ch):
    with open(f"{DB_INSERT_FN}{NAT_GEN_TN}.sql") as f:
        conn.execute(f.read(), [item_name, struct, cont, quant, ch])
    add_to_obtaining_table(
        conn, conn.cursor(), item_name, "natural generation", "generation_id", NAT_GEN_TN)


def add_trading_to_db(conn, item_name, villager, vill_level, emeralds, other):
    if vill_level == "" and other == "":
        with open(f"{DB_INSERT_FN}{TRADING_TN}_no_level_no_other.sql") as f:
            conn.execute(f.read(), [item_name, villager, emeralds])
    elif vill_level == "" and other != "":
        with open(f"{DB_INSERT_FN}{TRADING_TN}_other_item_no_level.sql") as f:
            conn.execute(f.read(), [item_name, villager, emeralds, other])
    elif vill_level != "" and other == "":
        with open(f"{DB_INSERT_FN}{TRADING_TN}_no_item_with_level.sql") as f:
            conn.execute(f.read(), [item_name, villager, vill_level, emeralds])
    else:
        with open(f"{DB_INSERT_FN}{TRADING_TN}_all_values.sql") as f:
            conn.execute(f.read(), [item_name, villager, vill_level, emeralds, other])
    conn.commit()
    add_to_obtaining_table(conn, conn.cursor(), item_name, "trading", "trading_id", TRADING_TN)


def reset_table(conn, cur, table_name):
    cur.execute(f"DROP TABLE IF EXISTS {table_name}")
    # print(f"dropped {table_name}")

    with open(f"{DB_S}{table_name}.sql") as f:
        conn.executescript(f.read())
    # print(f"schema added for {table_name}")
    conn.commit()


def reset_entire_db():
    conn = get_db()
    cur = conn.cursor()
    for table_name in ALL_TABLE_NAMES:
        reset_table(conn, cur, table_name)
    reset_table(conn, cur, "item_to_group")

    # TODO: update schema to use item_to_group as foreign key references.
    """ Move in item_to_group (previously block_to_group) as copied from the original database. """
    other_db = sqlite3.connect("block_adder_flask/db/minecraft.db")
    other_db_cursor = other_db.cursor()
    other_db_cursor.execute("SELECT * FROM block_to_group")
    all_items = other_db_cursor.fetchall()
    other_db.close()

    for row in all_items:
        cur.execute(
            """INSERT INTO item_to_group(item_name, item_group) VALUES (?, ?); """,
            [row[0], row[1]])
    conn.commit()


@click.command("init-db")
def init_db_command():
    """ Clear all existing tables. (besides item list)"""
    db = get_db()
    reset_entire_db()
    reset_table(db, db.cursor(), "item_to_group")


def init_app(app):
    app.teardown_appcontext(close_db)
    app.cli.add_command(init_db_command)

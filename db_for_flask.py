import sqlite3
from sqlite3 import PARSE_DECLTYPES, Row

from flask import g

DB_S = "db/scripts/schema/"
TRADING_TN = "item_trading"
OBTAINING_TN = "item_obtaining_method"
NAT_GEN_TN = "item_natural_generation"
DB_INSERT_FN = "db/scripts/insert_into/"


def get_db():
    if "db" not in g:
        print("Connecting for the first time")
        g.db = sqlite3.connect(
            "db/minecraft.db",
            detect_types=PARSE_DECLTYPES
        )
        g.db.row_factory = Row

    return g.db


def close_db(e=None):
    db = g.pop("db", None)
    if db is not None:
        db.close()


def add_to_obtaining_table(conn, cur, block_name, method_name, id_title, table_name):
    print(conn, cur, block_name, method_name, id_title, table_name)
    cur.execute(
        f'''SELECT {id_title} FROM {table_name} WHERE item_name = "{block_name}"'''
    )
    ids = [row[0] for row in cur.fetchall()]
    for i in ids:
        with open(f"{DB_INSERT_FN}{OBTAINING_TN}.sql") as f:
            print(block_name, method_name, i)
            conn.execute(f.read(), [block_name, method_name, i])

    conn.commit()


def add_trading_to_db(
        conn, block_name, villager, vill_level, emeralds, other) -> object:
    if vill_level == "" and other == "":
        with open(f"{DB_INSERT_FN}{TRADING_TN}_no_level_no_other.sql") as f:
            conn.execute(f.read(), [block_name, villager, emeralds])
    elif vill_level == "" and other != "":
        with open(f"{DB_INSERT_FN}{TRADING_TN}_other_item_no_level.sql") as f:
            conn.execute(f.read(), [block_name, villager, emeralds, other])
    elif vill_level != "" and other == "":
        with open(f"{DB_INSERT_FN}{TRADING_TN}_no_item_with_level.sql") as f:
            conn.execute(f.read(), [block_name, villager, vill_level, emeralds])
    else:
        with open(f"{DB_INSERT_FN}{TRADING_TN}_all_values.sql") as f:
            conn.execute(f.read(), [block_name, villager, vill_level, emeralds, other])
    conn.commit()

    # Add to obtaining table
    add_to_obtaining_table(conn, conn.cursor(), block_name, "trading", "trading_id", TRADING_TN)


def add_natural_gen_to_db(conn, block_name, struct, cont, quant, ch):
    with open(f"{DB_INSERT_FN}{NAT_GEN_TN}.sql") as f:
        conn.execute(f.read(), [block_name, struct, cont, quant, ch])
    add_to_obtaining_table(
        conn, conn.cursor(), block_name, "natural generation", "generation_id", NAT_GEN_TN)


def reset_table(conn, cur, table_name):
    cur.execute(f"DROP TABLE IF EXISTS {table_name}")
    print(f"dropped {table_name}")

    with open(f"{DB_S}{table_name}.sql") as f:
        conn.executescript(f.read())
    print(f"schema added for {table_name}")


if __name__ == '__main__':
    conn = sqlite3.connect("db/minecraft.db")
    cur = conn.cursor()
    # reset_table(conn, cur, TRADING_TN)
    conn.commit()
    cur.close()
    conn.close()

import sqlite3
from sqlite3 import PARSE_DECLTYPES, Row

from flask import current_app, g

DB_S = "block_adder_flask/db/scripts/schema/"
DB_INSERT_FN = "block_adder_flask/db/scripts/insert_into/"

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


def get_group(item_name):
    conn = get_db()
    cur = conn.cursor()
    cur.execute('''SELECT item_group FROM item_to_group WHERE item_name = ?''', (item_name,))
    return cur.fetchone()["item_group"]


def init_app(app):
    app.teardown_appcontext(close_db)
    # app.cli.add_command(init_db_command)

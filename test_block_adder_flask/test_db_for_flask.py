import sqlite3

import pytest

import block_adder_flask.db_for_flask as d

ITEM_NAME = "Testing Item"


def test_get_close_db(app):
    with app.app_context():
        db = d.get_db()
        assert db is d.get_db()

    with pytest.raises(sqlite3.ProgrammingError) as e:
        db.execute("SELECT 1")

    assert "closed" in str(e.value)


def test_get_group(app):
    with app.app_context():
        assert d.get_group(ITEM_NAME) == "Testing Group"


def test_get_group_no_group(app):
    with app.app_context():
        db = d.get_db()
        cur = db.cursor()
        cur.execute('''INSERT INTO item_to_group(item_name) VALUES ("ITEM_NAME_2")''')
        assert d.get_group("ITEM_NAME_2") is None

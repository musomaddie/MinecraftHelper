import sqlite3

import pytest

import block_adder_flask.db_for_flask as d

ITEM_NAME = "Testing Item"


def _get_just_added(cur, table_name):
    cur.execute(f'''SELECT * FROM {table_name} WHERE item_name = "{ITEM_NAME}"''')
    return cur.fetchall()


def _get_all_obtainment_methods(cur):
    cur.execute(f'''SELECT * FROM {d.OBTAINING_TN}''')
    return [r["method"] for r in cur.fetchall()]


def _get_obtaining_table(cur):
    cur.execute(f'''SELECT * FROM {d.OBTAINING_TN} WHERE item_name = "{ITEM_NAME}" ''')
    return cur.fetchall()


def test_get_close_db(app):
    with app.app_context():
        db = d.get_db()
        assert db is d.get_db()

    with pytest.raises(sqlite3.ProgrammingError) as e:
        db.execute("SELECT 1")

    assert "closed" in str(e.value)


def test_add_to_obtaining_table(app):
    with app.app_context():
        db = d.get_db()
        cur = db.cursor()
        with open(f"{d.DB_INSERT_FN}{d.BREAKING_TN}_all_values.sql") as f:
            db.execute(f.read(), [ITEM_NAME, True, True, "Axe"])
        cur.execute(f'''SELECT breaking_id FROM {d.BREAKING_TN} WHERE item_name = "{ITEM_NAME}"''')
        added_id = cur.fetchone()["breaking_id"]

        d.add_to_obtaining_table(
            db, cur, ITEM_NAME, "breaking", "breaking_id", d.BREAKING_TN)

        results = _get_obtaining_table(cur)

    assert len(results) == 1
    result = results[0]
    assert result["item_name"] == ITEM_NAME
    assert result["method"] == "breaking"
    assert result["generates"] == added_id


@pytest.mark.parametrize(
    ("requires_tool", "requires_silk", "fastest_tool",
     "expected_tool", "expected_silk", "expected_fastest"),
    (["tool_yes", "silk_yes", "Axe", True, True, True],
     ["tool_yes", "silk_yes", "", True, True, False],
     ["tool_yes", "silk_no", "", True, False, False],
     ["tool_no", "silk_no", "", False, False, False]))
def test_add_breaking_to_db(
        requires_tool,
        requires_silk,
        fastest_tool,
        expected_tool,
        expected_silk,
        expected_fastest,
        app):
    with app.app_context():
        db = d.get_db()
        d.add_breaking_to_db(db, ITEM_NAME, requires_tool, requires_silk, fastest_tool)
        results = _get_just_added(db.cursor(), d.BREAKING_TN)
        assert "breaking" in _get_all_obtainment_methods(db.cursor())

    assert len(results) == 1
    result = results[0]
    assert result["item_name"] == ITEM_NAME
    assert result["requires_tool"] == expected_tool
    assert result["requires_silk_touch"] == expected_silk
    if expected_fastest:
        assert result["fastest_tool"] == fastest_tool
    else:
        assert result["fastest_tool"] is None


def test_add_fishing_to_db(app):
    item_level = "Treasure"
    with app.app_context():
        db = d.get_db()
        d.add_fishing_to_db(db, ITEM_NAME, item_level)
        results = _get_just_added(db.cursor(), d.FISHING_TN)
        assert "fishing" in _get_all_obtainment_methods(db.cursor())

    assert len(results) == 1
    result = results[0]
    assert result["item_name"] == ITEM_NAME
    assert result["treasure_type"] == item_level


def test_add_nat_biome_to_db(app):
    biome = "Swamp"
    with app.app_context():
        db = d.get_db()
        d.add_nat_biome_to_db(db, ITEM_NAME, biome)
        results = _get_just_added(db.cursor(), d.NAT_BIOME_TN)
        assert "biome" in _get_all_obtainment_methods(db.cursor())

    assert len(results) == 1
    result = results[0]
    assert result["item_name"] == ITEM_NAME
    assert result["biome_name"] == biome


def test_add_natural_gen_to_db(app):
    struct = "testing struct"
    container = "testing container"
    quant = 1
    chance = 25
    with app.app_context():
        db = d.get_db()
        d.add_natural_gen_to_db(db, ITEM_NAME, struct, container, quant, chance)
        results = _get_just_added(db.cursor(), d.NAT_GEN_TN)
        assert "natural generation" in _get_all_obtainment_methods(db.cursor())

    assert len(results) == 1
    result = results[0]
    assert result["item_name"] == ITEM_NAME
    assert result["structure"] == struct
    assert result["container"] == container
    assert result["quantity"] == quant
    assert result["chance"] == chance


@pytest.mark.parametrize(
    ("villager", "v_level", "emeralds", "other", "expected_v_lvl", "expected_other"),
    ([("Testing Villager", "Testing Level", 13, "Testing Other", True, True),
      ("Testing Villager", "Testing LeveL", 13, "", True, False),
      ("Testing Villager", "", 13, "Testing Other", False, True),
      ("Testing Villager", "", 13, "", False, False)]
    ))
def test_add_trading_to_db(villager, v_level, emeralds, other, expected_v_lvl, expected_other, app):
    with app.app_context():
        db = d.get_db()
        d.add_trading_to_db(db, ITEM_NAME, villager, v_level, emeralds, other)
        results = _get_just_added(db.cursor(), d.TRADING_TN)
        assert "trading" in _get_all_obtainment_methods(db.cursor())

    assert len(results) == 1
    result = results[0]
    assert result["item_name"] == ITEM_NAME
    assert result["villager_type"] == villager
    assert result["emerald_price"] == emeralds
    if expected_v_lvl:
        assert result["villager_level"] == v_level
    else:
        assert result["villager_level"] is None
    if expected_other:
        assert result["other_price"] == other
    else:
        assert result["other_price"] is None

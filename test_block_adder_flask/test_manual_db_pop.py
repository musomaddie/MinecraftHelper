from unittest.mock import ANY, MagicMock, call, patch

import pytest

from block_adder_flask.manual_db_population import move_next_page, select_next_item

FILE_LOC = "block_adder_flask.manual_db_population"
ITEM_NAME = "Testing Item"


@pytest.mark.parametrize(
    ("item_name_list", "saved_items", "expected_name"),
    [([{"item_name": "Testing Item 1"}], [], "Testing Item 1"),
     ([{"item_name": "Testing Item 1"}, {"item_name": "Testing Item 2"}],
      [{"item_name": "Testing Item 1"}], "Testing Item 2")]
)
@patch(f"{FILE_LOC}.redirect")
@patch(f"{FILE_LOC}.url_for")
def test_select_next_block(
        mock_url_for, mock_redirect, item_name_list, saved_items, expected_name):
    mock_cursor = MagicMock()
    mock_cursor.fetchall.side_effect = [item_name_list, saved_items]
    select_next_item(mock_cursor)
    mock_url_for.assert_has_calls(
        [call("add.item", item_name=expected_name)])
    mock_redirect.assert_called_once()


@pytest.mark.parametrize(
    ("remaining_items", "first_item", "expected_remaining"),
    [(["breaking", "trading"], "breaking", ["trading"]),
     (["trading"], "trading", []),
     (["breaking", "trading", "fishing"], "breaking", ["trading", "fishing"])]
)
@patch(f"{FILE_LOC}.redirect")
@patch(f"{FILE_LOC}.url_for")
def test_move_next_page_with_items(
        mock_url_for, mock_redirect, remaining_items, first_item, expected_remaining):
    move_next_page(ITEM_NAME, remaining_items)
    mock_url_for.assert_has_calls(
        [call(first_item, item_name=ITEM_NAME, remaining_items=expected_remaining)])
    mock_redirect.assert_called_once()


@patch(f"{FILE_LOC}.select_next_item")
@patch(f"{FILE_LOC}.get_db")
def test_move_next_page_no_item_remaining(mock_get_db, mock_select_next_item):
    move_next_page(ITEM_NAME, [])
    mock_get_db.assert_has_calls([call().cursor()])
    mock_select_next_item.assert_called_once()


@patch(f"{FILE_LOC}.redirect")
@patch(f"{FILE_LOC}.url_for")
@patch(f"{FILE_LOC}.select_next_item")
@patch(f"{FILE_LOC}.get_db")
def test_move_next_page_string_list(
        mock_get_db, mock_select_next_item, mock_url_for, mock_redirection):
    move_next_page(ITEM_NAME, "[]")
    mock_get_db.assert_has_calls([call().cursor()])
    mock_select_next_item.assert_called_once()

    move_next_page(ITEM_NAME, "['breaking', 'trading']")
    mock_url_for.assert_called_once_with(
        "breaking", item_name=ITEM_NAME, remaining_items=["trading"])


@pytest.mark.parametrize(
    ("form_data", "expected_tool", "expected_silk", "expected_fastest"),
    [({"requires_tool": "tool_yes", "requires_silk": "silk_yes", "fastest_tool": "axe"},
      "tool_yes", "silk_yes", "axe"),
     ({"requires_tool": "tool_yes", "requires_silk": "silk_yes"},
      "tool_yes", "silk_yes", "")]
)
@patch(f"{FILE_LOC}.move_next_page")
@patch(f"{FILE_LOC}.add_breaking_to_db")
@patch(f"{FILE_LOC}.get_db")
@patch(f"{FILE_LOC}.flash")
def test_add_breaking(
        mock_flask, mock_get_db, mock_add_to_db, mock_move_next_page,
        form_data, expected_tool, expected_silk, expected_fastest, client):
    response = client.post(
        f"/add_breaking/{ITEM_NAME}/['trading']",
        data=form_data)
    assert response.status_code == 200
    mock_flask.assert_called_once_with(f"Successfully added {ITEM_NAME} to the breaking table")
    mock_get_db.assert_called_once()
    mock_add_to_db.assert_called_once_with(
        ANY, ITEM_NAME, expected_tool, expected_silk, expected_fastest)
    mock_move_next_page.assert_called_once_with(ITEM_NAME, "['trading']")


@patch(f"{FILE_LOC}.add_fishing_to_db")
@patch(f"{FILE_LOC}.get_db")
@patch(f"{FILE_LOC}.flash")
@patch(f"{FILE_LOC}.move_next_page")
def test_add_fishing(mock_move_next_page, mock_flash, mock_get_db, mock_add_to_db, client):
    response = client.post(
        f"/add_fishing/{ITEM_NAME}/['trading']",
        data={"item_level": "Treasure"})
    assert response.status_code == 200
    mock_add_to_db.assert_called_once_with(ANY, ITEM_NAME, "Treasure")
    mock_get_db.assert_called_once()
    mock_flash.assert_called_once_with(f"Successfully added {ITEM_NAME} to fishing")
    mock_move_next_page.assert_called_once_with(ITEM_NAME, "['trading']")


@patch(f"{FILE_LOC}.add_crafting_recipe_to_db")
@patch(f"{FILE_LOC}.get_db")
@patch(f"{FILE_LOC}.flash")
@patch(f"{FILE_LOC}.move_next_page")
def test_crafting(
        mock_move_next_page, mock_flash, mock_get_db, mock_add_to_db, client):
    response = client.post(
        f"/add_crafting/{ITEM_NAME}/['breaking']",
        data={"cs1": "Test Item 2", "n_created": 1, "next": True}
    )
    # TODO: add more params in here - more tests!
    assert response.status_code == 200
    mock_add_to_db.assert_called_once_with(
        ANY, ITEM_NAME, ["Test Item 2", "", "", "", "", "", "", "", ""], 1, "", "")
    mock_get_db.assert_called_once()
    mock_flash.assert_called_once_with(f"Successfully added {ITEM_NAME} to crafting")
    mock_move_next_page.assert_called_once_with(ITEM_NAME, "['breaking']")


@patch(f"{FILE_LOC}.add_crafting_recipe_to_db")
@patch(f"{FILE_LOC}.get_db")
@patch(f"{FILE_LOC}.flash")
@patch(f"{FILE_LOC}.redirect")
@patch(f"{FILE_LOC}.url_for")
def test_add_crafting_not_next(
        mock_url_for, mock_redirect, mock_flash, mock_get_db, mock_add_to_db, client):
    response = client.post(
        f"/add_crafting/{ITEM_NAME}/['breaking']",
        data={"cs1": "Test Item 2", "n_created": 1}
    )
    assert response.status_code == 200
    mock_add_to_db.assert_called_once_with(
        ANY, ITEM_NAME, ["Test Item 2", "", "", "", "", "", "", "", ""], 1, "", "")
    mock_get_db.assert_called_once()
    mock_flash.assert_called_once_with(f"Successfully added {ITEM_NAME} to crafting")
    mock_redirect.assert_called_once()
    mock_url_for.assert_called_once_with(
        "add.crafting", item_name=ITEM_NAME, remaining_items="['breaking']")


@patch(f"{FILE_LOC}.add_natural_gen_to_db")
@patch(f"{FILE_LOC}.get_db")
@patch(f"{FILE_LOC}.flash")
@patch(f"{FILE_LOC}.redirect")
@patch(f"{FILE_LOC}.url_for")
def test_add_natural_generation_not_next(
        mock_url_for,
        mock_redirect,
        mock_flash,
        mock_get_db,
        mock_add_to_db,
        client):
    response = client.post(
        f"/add_natural_generation/{ITEM_NAME}/['trading']",
        data={"structure": "Test Structure",
              "container": "Container",
              "quantity_fd": 1,
              "chance": 50})
    assert response.status_code == 200
    mock_add_to_db.assert_called_once_with(ANY, ITEM_NAME, "Test Structure", "Container", 1, 50)
    mock_flash.assert_called_once_with(
        f"Successfully added {ITEM_NAME} to natural generation table")
    mock_get_db.assert_called_once()
    mock_redirect.assert_called_once()
    mock_url_for.assert_called_once_with(
        "add.natural_generation", item_name=ITEM_NAME, remaining_items="['trading']")


@patch(f"{FILE_LOC}.add_natural_gen_to_db")
@patch(f"{FILE_LOC}.get_db")
@patch(f"{FILE_LOC}.flash")
@patch(f"{FILE_LOC}.move_next_page")
def test_add_natural_generation(
        mock_move_next_page, mock_flash, mock_get_db, mock_add_to_db, client):
    response = client.post(
        f"/add_natural_generation/{ITEM_NAME}/['trading']",
        data={"structure": "Test Structure",
              "container": "Container",
              "quantity_fd": 1,
              "next": True,
              "chance": 50})
    assert response.status_code == 200
    mock_add_to_db.assert_called_once_with(ANY, ITEM_NAME, "Test Structure", "Container", 1, 50)
    mock_get_db.assert_called_once()
    mock_flash.assert_called_once_with(
        f"Successfully added {ITEM_NAME} to natural generation table")
    mock_move_next_page.assert_called_once_with(ITEM_NAME, "['trading']")


@patch(f"{FILE_LOC}.add_nat_biome_to_db")
@patch(f"{FILE_LOC}.get_db")
@patch(f"{FILE_LOC}.flash")
@patch(f"{FILE_LOC}.move_next_page")
def test_add_natural_generation_biome(
        mock_move_next_page, mock_flash, mock_get_db, mock_add_to_db, client):
    response = client.post(f"/add_natural_biome/{ITEM_NAME}/['trading']", data={"biome": "Swamp"})
    assert response.status_code == 200
    mock_add_to_db.assert_called_once_with(ANY, ITEM_NAME, "Swamp")
    mock_get_db.assert_called_once()
    mock_flash.assert_called_once_with(f"Successfully added {ITEM_NAME} to biome")
    mock_move_next_page.assert_called_once_with(ITEM_NAME, "['trading']")


@pytest.mark.parametrize(
    ("form_data", "expected_lvl", "expected_other"),
    [({"villager_type": "Test Villager", "emerald_price": 10,
       "villager_level": "Test Level", "other_item": "Test Other"}, "Test Level", "Test Other"),
     ({"villager_type": "Test Villager", "emerald_price": 10, "villager_level": "Test Level"},
      "Test Level", ""),
     ({"villager_type": "Test Villager", "emerald_price": 10, "other_item": "Test Other"},
      "", "Test Other"),
     ({"villager_type": "Test Villager", "emerald_price": 10}, "", "")
     ])
@patch(f"{FILE_LOC}.add_trading_to_db")
@patch(f"{FILE_LOC}.get_db")
@patch(f"{FILE_LOC}.flash")
@patch(f"{FILE_LOC}.move_next_page")
def test_add_trading(
        mock_move_next_page,
        mock_flash,
        mock_get_db,
        mock_add_to_db,
        form_data,
        expected_lvl,
        expected_other,
        client):
    response = client.post(f"/add_trading/{ITEM_NAME}/['breaking']", data=form_data)
    assert response.status_code == 200
    mock_add_to_db.assert_called_once_with(
        ANY, ITEM_NAME, "Test Villager", expected_lvl, 10, expected_other)
    mock_flash.assert_called_once_with(f"Successfully added {ITEM_NAME} to trading table.")
    mock_move_next_page.assert_called_once_with(ITEM_NAME, "['breaking']")


@patch(f"{FILE_LOC}.move_next_page")
def test_add_item(mock_move_next_page, client):
    response = client.post(
        f"/add_item/{ITEM_NAME}",
        data={"trading": "", "nat_gen": "", "breaking": "", "fishing": "", "nat_biome": ""})
    assert response.status_code == 200
    mock_move_next_page.assert_called_once_with(
        ITEM_NAME,
        ["add.trading", "add.natural_generation", "add.breaking", "add.fishing",
         "add.natural_biome"])

import json
from unittest.mock import call, patch

import pytest
from _pytest.fixtures import fixture

import block_adder_flask.manual_db_population as pop

ITEM_NAME = "Test Item"

FILE_LOC = "block_adder_flask.manual_db_population"
EXPECTED_JSON_DIR = "block_adder_flask/item_information"
REMAINING_ITEMS = "['breaking']"


@fixture
def tmp_json_file_no_items(tmpdir):
    filename = tmpdir.join("test.json")
    with open(filename, "w") as f:
        json.dump({"items": []}, f)
    return filename


def test_update_json_file(tmpdir):
    file = tmpdir.join("test.json")
    pop._update_json_file({"Testing": True}, file)
    with open(file) as f:
        result = json.load(f)
    assert result["Testing"]


def test_get_all_json_files_no_files(tmp_json_file_no_items):
    assert len(pop._get_all_items_json_file(tmp_json_file_no_items)) == 0


def test_get_all_json_files_with_data(tmpdir):
    file = tmpdir.join("testing_all_items.json")
    with open(file, "w") as f:
        json.dump({"items": ["T1"]}, f)
    result = pop._get_all_items_json_file(file)
    assert len(result) == 1
    assert result[0] == "T1"


def test_add_to_item_list(tmp_json_file_no_items):
    pop._add_to_item_list(ITEM_NAME, tmp_json_file_no_items)
    with open(tmp_json_file_no_items) as f:
        created_json = json.load(f)
        assert len(created_json["items"]) == 1
        assert created_json["items"][0] == ITEM_NAME


@pytest.mark.parametrize(
    ("from_db", "json_data", "expected_name"),
    [("DB Group", {}, "DB Group"),
     ("", {"group": "Json Group"}, "Json Group"),
     ("DB Group", {"group": "Json Group"}, "Json Group")])
def test_get_updated_group_name(from_db, json_data, expected_name):
    assert pop._get_updated_group_name(from_db, json_data) == expected_name


@patch(f"{FILE_LOC}._update_json_file")
@patch(f"{FILE_LOC}._get_file_contents")
def test_append_json(mock_get_file_contents, mock_update_json_file, tmp_json_file_no_items):
    mock_get_file_contents.return_value = {"name": ITEM_NAME}
    pop._append_json_file("test key", {"item 1": 45, "item 2": True}, tmp_json_file_no_items)
    mock_update_json_file.assert_called_once_with(
        {"name": ITEM_NAME, "test key": {"item 1": 45, "item 2": True}}, tmp_json_file_no_items)


@patch(f"{FILE_LOC}._update_json_file")
@patch(f"{FILE_LOC}._get_file_contents")
def test_append_json_key_exists(
        mock_get_file_contents, mock_update_json_file, tmp_json_file_no_items):
    mock_get_file_contents.return_value = {
        "name": ITEM_NAME, "new key": {"item 1": "45", "item 2": 45}}
    pop._append_json_file(
        "new key", {"item 1a": "thing", "item 2a": "thing 2"},
        tmp_json_file_no_items)
    mock_update_json_file.assert_called_once_with(
        {"name": ITEM_NAME, "new key":
            [{"item 1": "45", "item 2": 45}, {"item 1a": "thing", "item 2a": "thing 2"}]},
        tmp_json_file_no_items
    )


# ##################################################################################################
#                            item                                                                  #
# ##################################################################################################

@patch(f"{FILE_LOC}.join")
@patch(f"{FILE_LOC}.isfile")
@patch(f"{FILE_LOC}._get_file_contents")
@patch(f"{FILE_LOC}._add_to_item_list")
@patch(f"{FILE_LOC}.get_group")
def test_add_item_get_file_exists_with_mocks(
        mock_get_group,
        mock_add_to_item_list,
        mock_get_file_contents,
        mock_isfile,
        mock_join,
        client):
    # if isfile(join(JSON_DIR, item_file_name)):
    #     # TODO: rewrite to use reading helper
    #     existing_json_data = _get_file_contents(item_file_name_full)
    #     _add_to_item_list(item_name)
    mock_isfile.return_value = True
    mock_get_group.return_value = "Testing Group"
    response = client.get(f"/add_item/{ITEM_NAME}")
    assert response.status_code == 200
    mock_join.assert_called_once_with("block_adder_flask/item_information", "Test Item.json")
    mock_isfile.assert_called_once()
    mock_get_file_contents.assert_called_once_with(f"{EXPECTED_JSON_DIR}/{ITEM_NAME}.json")
    mock_add_to_item_list.assert_called_once_with(ITEM_NAME)


@patch(f"{FILE_LOC}.join")
@patch(f"{FILE_LOC}.isfile")
@patch(f"{FILE_LOC}._update_json_file")
@patch(f"{FILE_LOC}.get_group")
def test_add_item_get_doesnt_already_exist_with_mocks(
        mock_get_group, mock_update_json_file, mock_isfile, mock_join, app, client):
    mock_isfile.return_value = False
    mock_get_group.return_value = "Testing Group"
    response = client.get(f"/add_item/{ITEM_NAME}")
    assert response.status_code == 200
    mock_join.assert_called_once_with("block_adder_flask/item_information", "Test Item.json")
    mock_isfile.assert_called_once()
    mock_update_json_file.assert_called_once_with(
        {"name": ITEM_NAME}, f"{EXPECTED_JSON_DIR}/{ITEM_NAME}.json")


@patch(f"{FILE_LOC}.join")
@patch(f"{FILE_LOC}.isfile")
@patch(f"{FILE_LOC}.open")
@patch(f"{FILE_LOC}.get_group")
@patch(f"{FILE_LOC}._get_updated_group_name")
@patch(f"{FILE_LOC}._update_json_file")
def test_add_item_update_group(
        mock_update_file,
        mock_get_group_name,
        mock_get_group,
        mock_open,
        mock_isfile,
        mock_join,
        client):
    mock_isfile.return_value = False
    response = client.post(
        f"/add_item/{ITEM_NAME}",
        data={"update_group": True, "group_name_replacement": "New Group"})
    assert response.status_code == 200
    mock_get_group.assert_called_once_with(ITEM_NAME)
    mock_update_file.assert_has_calls(
        [call(
            {"name": "Test Item", "group": "New Group"},
            f"{EXPECTED_JSON_DIR}/{ITEM_NAME}.json"),
            call(
                {"name": "Test Item", "group": "New Group"},
                f"{EXPECTED_JSON_DIR}/{ITEM_NAME}.json")
        ])


@patch(f"{FILE_LOC}.join")
@patch(f"{FILE_LOC}._get_file_contents")
@patch(f"{FILE_LOC}._add_to_item_list")
@patch(f"{FILE_LOC}.isfile")
@patch(f"{FILE_LOC}.open")
@patch(f"{FILE_LOC}.get_group")
@patch(f"{FILE_LOC}._get_updated_group_name")
@patch(f"{FILE_LOC}._update_json_file")
@patch(f"{FILE_LOC}.move_next_page")
def test_add_item_post(
        mock_move_next_page, mock_update_json_file, mock_get_updated_group_name, mock_get_group,
        mock_open, mock_isfile, mock_add_to_item_list, mock_file_contents, mock_join, client):
    mock_isfile = False
    response = client.post(
        f"/add_item/{ITEM_NAME}",
        data={"trading": "", "nat_gen": "", "breaking": "", "fishing": "", "nat_biome": "",
              "crafting": "", "nat_struct": ""})
    assert response.status_code == 200
    mock_move_next_page.assert_called_once_with(
        ITEM_NAME,
        ["add.breaking", "add.crafting", "add.fishing", "add.trading", "add.natural_generation",
         "add.natural_generation_biome", "add.natural_gen_structure"])


# ##################################################################################################
#                            breaking                                                              #
# ##################################################################################################
@pytest.mark.parametrize(
    ("requires_tool", "expected_tool", "requires_silk", "expected_silk",
     "has_tool", "fastest_tool"),
    [("tool_no", False, "silk_no", False, False, ""),
     ("tool_no", False, "silk_no", False, True, "Fastest Tool"),
     ("tool_yes", True, "silk_no", False, False, ""),
     ("tool_yes", True, "silk_no", False, True, "Fastest Tool"),
     ("tool_no", False, "silk_yes", True, False, ""),
     ("tool_no", False, "silk_yes", True, True, ""),
     ("tool_yes", True, "silk_yes", True, False, ""),
     ("tool_yes", True, "silk_yes", True, True, "")])
@patch(f"{FILE_LOC}._append_json_file")
@patch(f"{FILE_LOC}.flash")
@patch(f"{FILE_LOC}.move_next_page")
def test_breaking(
        mock_move_next_page, mock_flash, mock_append_json_file,
        requires_tool, expected_tool, requires_silk, expected_silk, has_tool, fastest_tool, client):
    form_data = {"requires_tool": requires_tool, "requires_silk": requires_silk, }
    expected_data = {
        "requires tool": expected_tool,
        "requires silk": expected_silk,
        "fastest tool": fastest_tool if has_tool else ""
    }
    if has_tool:
        form_data["fastest_tool"] = fastest_tool
    response = client.post(f"/add_breaking/{ITEM_NAME}/{REMAINING_ITEMS}", data=form_data)
    assert response.status_code == 200
    mock_append_json_file.assert_called_once_with(
        "breaking", expected_data, f"{EXPECTED_JSON_DIR}/{ITEM_NAME}.json")
    mock_flash.assert_called_once()
    mock_move_next_page.assert_called_once_with(ITEM_NAME, REMAINING_ITEMS)


# ##################################################################################################
#                            crafting                                                              #
# ##################################################################################################
@patch(f"{FILE_LOC}._append_json_file")
@patch(f"{FILE_LOC}.flash")
@patch(f"{FILE_LOC}.redirect")
@patch(f"{FILE_LOC}.url_for")
def test_crafting(mock_url_for, mock_redirect, mock_flash, mock_append_json_file, client):
    form_data = {
        "cs1": "Item 1", "cs2": "Item 2", "cs3": "Item 3", "cs4": "Item 4", "cs5": "Item 5",
        "cs6": "Item 6", "cs7": "Item 7", "cs8": "Item 8", "cs9": "Item 9",
        "n_created": 1, "works_four": "", "exact_positioning": ""
    }
    expected_data = {
        "crafting slots":
            ["Item 1", "Item 2", "Item 3", "Item 4", "Item 5", "Item 6", "Item 7", "Item 8",
             "Item 9"],
        "num created": 1,
        "works with four by four": True,
        "requires exact positioning": True
    }
    response = client.post(f"/add_crafting/{ITEM_NAME}/{REMAINING_ITEMS}", data=form_data)
    assert response.status_code == 200
    mock_append_json_file.assert_called_once_with(
        "crafting", expected_data, f"{EXPECTED_JSON_DIR}/{ITEM_NAME}.json")
    mock_flash.assert_called_once()
    mock_redirect.assert_called_once()
    mock_url_for.assert_called_once_with(
        "add.crafting", item_name=ITEM_NAME, remaining_items=REMAINING_ITEMS)


@patch(f"{FILE_LOC}._append_json_file")
@patch(f"{FILE_LOC}.flash")
@patch(f"{FILE_LOC}.move_next_page")
def test_crafting_move_next(mock_move_next_page, mock_flash, mock_append_json, client):
    # Also testing with a not full crafting grid and without some booleans
    form_data = {
        "cs1": "Item 1", "cs3": "Item 2", "cs4": "Item 3", "cs5": "Item 4",
        "n_created": "1", "exact_positioning": "", "next": ""
    }
    expected_data = {
        "crafting slots": [
            "Item 1", "", "Item 2", "Item 3", "Item 4", "", "", "", ""],
        "num created": 1,
        "works with four by four": False,
        "requires exact positioning": True
    }
    response = client.post(f"/add_crafting/{ITEM_NAME}/{REMAINING_ITEMS}", data=form_data)
    assert response.status_code == 200
    mock_append_json.assert_called_once_with(
        "crafting", expected_data, f"{EXPECTED_JSON_DIR}/{ITEM_NAME}.json")
    mock_flash.assert_called_once()
    mock_move_next_page.assert_called_once_with(ITEM_NAME, REMAINING_ITEMS)


# ##################################################################################################
#                            fishing                                                               #
# ##################################################################################################
@patch(f"{FILE_LOC}._append_json_file")
@patch(f"{FILE_LOC}.flash")
@patch(f"{FILE_LOC}.move_next_page")
def test_fishing(mock_move_next_page, mock_flash, mock_append_json_file, client):
    response = client.post(
        f"/add_fishing/{ITEM_NAME}/{REMAINING_ITEMS}", data={"item_level": "Treasure"})
    assert response.status_code == 200
    mock_append_json_file.assert_called_once_with(
        "fishing", {"treasure type": "Treasure"}, f"{EXPECTED_JSON_DIR}/{ITEM_NAME}.json")
    mock_flash.assert_called_once()
    mock_move_next_page.assert_called_once_with(ITEM_NAME, REMAINING_ITEMS)


# ##################################################################################################
#                            chest generation                                                      #
# ##################################################################################################

@pytest.mark.parametrize(
    ("has_container", "expected_container", "has_chance", "expected_chance"),
    [(True, "Container 1", True, 50),
     (True, "Container 1", False, 100),
     (False, "", True, 50),
     (False, "", False, 100)]
)
@patch(f"{FILE_LOC}._append_json_file")
@patch(f"{FILE_LOC}.flash")
@patch(f"{FILE_LOC}.url_for")
@patch(f"{FILE_LOC}.redirect")
def test_natural_generation(
        mock_redirect, mock_url_for, mock_flash, mock_append_json_file,
        has_container, expected_container, has_chance, expected_chance, client):
    form_data = {"structure": "Structure 1", "quantity_fd": 1}
    expected_data = {"structure": "Structure 1",
                     "container": "",
                     "quantity": 1,
                     "chance": 100}
    if has_container:
        form_data["container"] = expected_container
        expected_data["container"] = expected_container
    if has_chance:
        form_data["chance"] = expected_chance
        expected_data["chance"] = expected_chance

    response = client.post(f"/add_natural_generation/{ITEM_NAME}/{REMAINING_ITEMS}", data=form_data)
    assert response.status_code == 200
    mock_append_json_file.assert_called_once_with(
        "generated in chests", expected_data, f"{EXPECTED_JSON_DIR}/{ITEM_NAME}.json")
    mock_flash.assert_called_once()
    mock_url_for.assert_called_once_with(
        "add.natural_generation", item_name=ITEM_NAME, remaining_items=REMAINING_ITEMS)
    mock_redirect.assert_called_once()


@patch(f"{FILE_LOC}._append_json_file")
@patch(f"{FILE_LOC}.flash")
@patch(f"{FILE_LOC}.move_next_page")
def test_natural_generation_move_next(
        mock_move_next_page, mock_flash, mock_append_json_file, client):
    response = client.post(
        f"/add_natural_generation/{ITEM_NAME}/{REMAINING_ITEMS}",
        data={"structure": "Structure 1", "quantity_fd": 2, "next": ""})
    assert response.status_code == 200
    mock_append_json_file.assert_called_once_with(
        "generated in chests",
        {"structure": "Structure 1", "container": "", "quantity": 2, "chance": 100},
        f"{EXPECTED_JSON_DIR}/{ITEM_NAME}.json")
    mock_flash.assert_called_once()
    mock_move_next_page.assert_called_once_with(ITEM_NAME, REMAINING_ITEMS)

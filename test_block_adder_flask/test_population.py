import json
from unittest.mock import call, patch

import pytest
from _pytest.fixtures import fixture

import block_adder_flask.manual_db_population as pop

ITEM_NAME = "Test Item"

FILE_LOC = "block_adder_flask.manual_db_population"


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
    assert pop.get_updated_group_name(from_db, json_data) == expected_name


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
    mock_get_file_contents.assert_called_once_with(
        "block_adder_flask/item_information/Test Item.json")
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
        {"name": ITEM_NAME}, "block_adder_flask/item_information/Test Item.json")


@patch(f"{FILE_LOC}.join")
@patch(f"{FILE_LOC}.isfile")
@patch(f"{FILE_LOC}.open")
@patch(f"{FILE_LOC}.get_group")
@patch(f"{FILE_LOC}.get_updated_group_name")
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
            "block_adder_flask/item_information/Test Item.json"),
            call(
                {"name": "Test Item", "group": "New Group"},
                "block_adder_flask/item_information/Test Item.json")
        ])


@patch(f"{FILE_LOC}.join")
@patch(f"{FILE_LOC}._get_file_contents")
@patch(f"{FILE_LOC}._add_to_item_list")
@patch(f"{FILE_LOC}.isfile")
@patch(f"{FILE_LOC}.open")
@patch(f"{FILE_LOC}.get_group")
@patch(f"{FILE_LOC}.get_updated_group_name")
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

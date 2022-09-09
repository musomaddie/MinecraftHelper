from unittest.mock import patch

import pytest

import block_adder_flask.get_group_info as gg

ITEM_NAME = "Test Item"
GROUP_NAME = "Test Group"
EXPECTED_JSON_DIR = "block_adder_flask/item_information"
FILE_LOC = "block_adder_flask.get_group_info"


@pytest.mark.parametrize(
    ("from_db", "json_data", "expected_name"),
    [("DB Group", {}, "DB Group"),
     ("", {"group": "Json Group"}, "Json Group"),
     (None, {}, ""),
     ("DB Group", {"group": "Json Group"}, "Json Group")])
def test_get_updated_group_name(from_db, json_data, expected_name):
    assert gg.get_updated_group_name(
        from_db, json_data) == expected_name

@patch(f"{FILE_LOC}.isfile")
@patch(f"{FILE_LOC}.update_json_file")
def test_save_to_group_new_group(mock_update_json_file, mock_isfile):
    mock_isfile.return_value = False
    gg.save_to_group(GROUP_NAME, ITEM_NAME)
    mock_update_json_file.assert_called_once_with(
        {"group name": GROUP_NAME, "items": [ITEM_NAME]},
        f"{EXPECTED_JSON_DIR}/groups/{GROUP_NAME}.json"
    )

@patch(f"{FILE_LOC}.isfile")
@patch(f"{FILE_LOC}.get_file_contents")
@patch(f"{FILE_LOC}.update_json_file")
def test_save_to_group_already_in_group(mock_update_json_file, mock_get_file_contents, mock_isfile):
    mock_isfile.return_value = True
    mock_get_file_contents.return_value = {"group name": GROUP_NAME, "items": [ITEM_NAME]}
    gg.save_to_group(GROUP_NAME, ITEM_NAME)
    mock_update_json_file.assert_not_called()


@patch(f"{FILE_LOC}.isfile")
@patch(f"{FILE_LOC}.update_json_file")
def test_save_to_group_empty_group_name(mock_update_json_file, mock_isfile):
    gg.save_to_group("", ITEM_NAME)
    mock_isfile.assert_not_called()
    mock_update_json_file.assert_not_called()


@patch(f"{FILE_LOC}.isfile")
@patch(f"{FILE_LOC}.update_json_file")
def test_save_to_group_none_group_name(mock_update_json_file, mock_isfile):
    gg.save_to_group(None, ITEM_NAME)
    mock_isfile.assert_not_called()
    mock_update_json_file.assert_not_called()


@patch(f"{FILE_LOC}.isfile")
@patch(f"{FILE_LOC}.get_file_contents")
@patch(f"{FILE_LOC}.update_json_file")
def test_save_to_group_existing_group(mock_update_json_file, mock_get_file_contents, mock_isfile):
    mock_isfile.return_value = True
    mock_get_file_contents.return_value = {"group name": GROUP_NAME, "items": ["existing item"]}
    gg.save_to_group(GROUP_NAME, ITEM_NAME)
    mock_update_json_file.assert_called_once_with(
        {"group name": GROUP_NAME, "items": ["existing item", ITEM_NAME]},
        f"{EXPECTED_JSON_DIR}/groups/{GROUP_NAME}.json")


@pytest.mark.parametrize("group_name", [None, "", "None"])
def test_should_show_group_button_missing_group_name(group_name):
    assert not gg.should_show_group_button(group_name, "")


@patch(f"{FILE_LOC}.get_file_contents")
def test_should_show_group_button_only_item_in_group(mock_get_file_contents):
    mock_get_file_contents.return_value = {"group name": GROUP_NAME, "items": [ITEM_NAME]}
    assert not gg.should_show_group_button(GROUP_NAME, ITEM_NAME)


@patch(f"{FILE_LOC}.get_file_contents")
def test_should_show_group_button_true(mock_get_file_contents):
    mock_get_file_contents.return_value = {"group name": GROUP_NAME, "items": [ITEM_NAME, "Item 2"]}
    assert gg.should_show_group_button(GROUP_NAME, ITEM_NAME)


@patch(f"{FILE_LOC}.get_file_contents")
@patch(f"{FILE_LOC}.update_json_file")
def test_remove_from_group(mock_update_json_file, mock_get_file_contents):
    mock_get_file_contents.return_value = {
        "group name": GROUP_NAME, "items": ["Existing Item", ITEM_NAME]}
    gg.remove_from_group(GROUP_NAME, ITEM_NAME)
    mock_update_json_file.assert_called_once_with(
        {"group name": GROUP_NAME, "items": ["Existing Item"]},
        f"{EXPECTED_JSON_DIR}/groups/{GROUP_NAME}.json")


@patch(f"{FILE_LOC}.get_file_contents")
@patch(f"{FILE_LOC}.os.remove")
def test_remove_from_group_only_item(mock_remove, mock_get_file_contents):
    mock_get_file_contents.return_value = {"group name": GROUP_NAME, "items": [ITEM_NAME]}
    gg.remove_from_group(GROUP_NAME, ITEM_NAME)
    mock_remove.assert_called_once_with(f"{EXPECTED_JSON_DIR}/groups/{GROUP_NAME}.json")


@patch(f"{FILE_LOC}.get_file_contents")
def test_remove_from_group_no_group(mock_get_file_contents):
    gg.remove_from_group("", ITEM_NAME)
    mock_get_file_contents.assert_not_called()


@patch(f"{FILE_LOC}.get_file_contents")
def test_remove_from_group_none_group_name(mock_get_file_contents):
    gg.remove_from_group(None, ITEM_NAME)
    mock_get_file_contents.assert_not_called()

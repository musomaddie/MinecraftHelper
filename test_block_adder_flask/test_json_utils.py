import json
from unittest.mock import patch

import pytest

import block_adder_flask.json_utils as j_utils

ITEM_NAME = "Test Item"
FILE_LOC = "block_adder_flask.json_utils"
FILENAME = "block_adder_flask/item_information/FAKE FILENAME.json"


@pytest.fixture
def tmp_json_file_no_items(tmpdir):
    filename = tmpdir.join("test.json")
    with open(filename, "w") as f:
        json.dump({"items": []}, f)
    return filename


def test_update_json_file(tmpdir):
    file = tmpdir.join("test.json")
    j_utils.update_json_file({"Testing": True}, file)
    with open(file) as f:
        result = json.load(f)
    assert result["Testing"]


@patch(f"{FILE_LOC}.open")
@patch(f"{FILE_LOC}.json.load")
def test_get_all_json_files_no_files(mock_json_load, mock_open):
    mock_json_load.return_value = {"items": []}
    j_utils.get_all_items_json_file()
    mock_open.assert_called_once_with("block_adder_flask/item_information/item_list.json")


def test_get_all_json_files_with_data(tmpdir):
    file = tmpdir.join("testing_all_items.json")
    with open(file, "w") as f:
        json.dump({"items": ["T1"]}, f)
    result = j_utils.get_all_items_json_file(file)
    assert len(result) == 1
    assert result[0] == "T1"


@patch(f"{FILE_LOC}.update_json_file")
@patch(f"{FILE_LOC}.get_file_contents")
def test_append_json(mock_get_file_contents, mock_update_json_file):
    mock_get_file_contents.return_value = {"name": ITEM_NAME}
    j_utils.append_json_file(
        "test key", [("item 1", 45), ("item 2", True)], FILENAME)
    mock_update_json_file.assert_called_once_with(
        {"name": ITEM_NAME, "test key": {"item 1": 45, "item 2": True}}, FILENAME)


@patch(f"{FILE_LOC}.update_json_file")
@patch(f"{FILE_LOC}.get_file_contents")
def test_append_json_key_exists(
        mock_get_file_contents, mock_update_json_file):
    mock_get_file_contents.return_value = {
        "name": ITEM_NAME, "new key": {"item 1": "45", "item 2": 45}}
    j_utils.append_json_file(
        "new key",
        [("item 1a", "thing"), ("item 2a", "thing2")],
        FILENAME)
    mock_update_json_file.assert_called_once_with(
        {"name": ITEM_NAME, "new key":
            [{"item 1": "45", "item 2": 45}, {"item 1a": "thing", "item 2a": "thing2"}]},
        FILENAME)


@patch(f"{FILE_LOC}.update_json_file")
@patch(f"{FILE_LOC}.get_file_contents")
def test_append_json_condition_false(
        mock_get_file_contents, mock_update_json_file):
    mock_get_file_contents.return_value = {"name": ITEM_NAME}
    j_utils.append_json_file(
        "test key", [("item 1", "no condition"), ("item 2", "true condition", True),
                     ("item 3", "false condition", False)], FILENAME)
    mock_update_json_file.assert_called_once_with(
        {"name": ITEM_NAME, "test key": {"item 1": "no condition", "item 2": "true condition"}},
        FILENAME)

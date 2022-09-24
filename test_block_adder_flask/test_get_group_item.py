from unittest.mock import ANY, call, patch

import pytest

from block_adder_flask.get_group_info import (
    AlreadyEnteredGroupInformation, GroupInfoBuilder,
    get_updated_group_name, remove_from_group, save_to_group)

ITEM_NAME = "Test Item"
OTHER_ITEM_NAME = "Test Other Item"
GROUP_NAME = "Test Group"
EXPECTED_JSON_DIR = "block_adder_flask/item_information"
FILE_LOC = "block_adder_flask.get_group_info"
MOCK_ITEM_CONTENTS = {
    "name": ITEM_NAME,
    "group": GROUP_NAME,
    "breaking": {"sub key 1": "data", "sub key 2": ""},
    "crafting": {"more data"}
}


def test_group_init_builder():
    builder = GroupInfoBuilder(GROUP_NAME, ITEM_NAME)
    assert builder.group_name == GROUP_NAME
    assert builder.current_item == ITEM_NAME
    assert builder.other_items == []
    assert not builder.should_show
    assert builder.other_item_info == {}

    builder.set_other_items([OTHER_ITEM_NAME])
    assert builder.other_items == [OTHER_ITEM_NAME]
    builder.set_should_show(True)
    assert builder.should_show
    builder.set_other_item_info({"name": OTHER_ITEM_NAME})
    assert builder.other_item_info == {"name": OTHER_ITEM_NAME}

    created_group = builder.build()
    assert created_group.group_name == GROUP_NAME
    assert created_group.current_item == ITEM_NAME
    assert created_group.other_items == [OTHER_ITEM_NAME]
    assert created_group.should_show
    assert created_group.other_item_info == {"name": OTHER_ITEM_NAME}


@pytest.fixture
def existing_group_info():
    return AlreadyEnteredGroupInformation(
        GROUP_NAME, ITEM_NAME, [OTHER_ITEM_NAME], True,
        {"group name": GROUP_NAME, "items": [ITEM_NAME, OTHER_ITEM_NAME]})


@patch(f"{FILE_LOC}.get_file_contents", return_value={"items": [ITEM_NAME, OTHER_ITEM_NAME]})
def test_get_group_item(mock_get_file_contents, existing_group_info):
    assert AlreadyEnteredGroupInformation.get_group_items(GROUP_NAME, ITEM_NAME) == [
        OTHER_ITEM_NAME]
    mock_get_file_contents.assert_called_once_with(f"{EXPECTED_JSON_DIR}/groups/{GROUP_NAME}.json")


@patch(f"{FILE_LOC}.AlreadyEnteredGroupInformation")
@patch(f"{FILE_LOC}.get_file_contents")
def test_create_first_time(mock_get_file_contents, mock_existing_group_info):
    AlreadyEnteredGroupInformation.create_first_time(GROUP_NAME, ITEM_NAME)
    mock_existing_group_info.assert_has_calls(
        [call.get_group_items(GROUP_NAME, ITEM_NAME),
         call.get_group_items().__getitem__(0),
         ANY,
         call(GROUP_NAME, ITEM_NAME, ANY, True, ANY)]
    )


@patch(f"{FILE_LOC}.AlreadyEnteredGroupInformation")
def test_create_from_dict(mock_existing_group_info):
    AlreadyEnteredGroupInformation.create_from_dict(
        {"group_name": GROUP_NAME, "current_item": ITEM_NAME, "should_show": True,
         "other_items": [OTHER_ITEM_NAME], "other_item_info": MOCK_ITEM_CONTENTS}
    )
    mock_existing_group_info.assert_called_once_with(
        GROUP_NAME, ITEM_NAME, [OTHER_ITEM_NAME], True, MOCK_ITEM_CONTENTS)


@patch(f"{FILE_LOC}.get_file_contents")
@patch(f"{FILE_LOC}.update_json_file")
def test_remove_from_group(mock_update_json_file, mock_get_file_contents):
    mock_get_file_contents.return_value = {
        "group name": GROUP_NAME, "items": ["Existing Item", ITEM_NAME]}
    remove_from_group(GROUP_NAME, ITEM_NAME)
    mock_update_json_file.assert_called_once_with(
        {"group name": GROUP_NAME, "items": ["Existing Item"]},
        f"{EXPECTED_JSON_DIR}/groups/{GROUP_NAME}.json")


@patch(f"{FILE_LOC}.get_file_contents")
@patch(f"{FILE_LOC}.os.remove")
def test_remove_from_group_only_item(mock_remove, mock_get_file_contents):
    mock_get_file_contents.return_value = {"group name": GROUP_NAME, "items": [ITEM_NAME]}
    remove_from_group(GROUP_NAME, ITEM_NAME)
    mock_remove.assert_called_once_with(f"{EXPECTED_JSON_DIR}/groups/{GROUP_NAME}.json")


@patch(f"{FILE_LOC}.get_file_contents")
def test_remove_from_group_no_group(mock_get_file_contents):
    remove_from_group("", ITEM_NAME)
    mock_get_file_contents.assert_not_called()


@patch(f"{FILE_LOC}.get_file_contents")
def test_remove_from_group_none_group_name(mock_get_file_contents):
    remove_from_group(None, ITEM_NAME)
    mock_get_file_contents.assert_not_called()


@patch(f"{FILE_LOC}.isfile")
@patch(f"{FILE_LOC}.update_json_file")
def test_save_to_group_new_group(mock_update_json_file, mock_isfile):
    mock_isfile.return_value = False
    save_to_group(GROUP_NAME, ITEM_NAME)
    mock_update_json_file.assert_called_once_with(
        {"group name": GROUP_NAME, "items": [ITEM_NAME]},
        f"{EXPECTED_JSON_DIR}/groups/{GROUP_NAME}.json"
    )


@patch(f"{FILE_LOC}.isfile")
@patch(f"{FILE_LOC}.get_file_contents")
@patch(f"{FILE_LOC}.update_json_file")
def test_save_to_group_already_in_group(
        mock_update_json_file, mock_get_file_contents,
        mock_isfile):
    mock_isfile.return_value = True
    mock_get_file_contents.return_value = {"group name": GROUP_NAME, "items": [ITEM_NAME]}
    save_to_group(GROUP_NAME, ITEM_NAME)
    mock_update_json_file.assert_not_called()


@patch(f"{FILE_LOC}.isfile")
@patch(f"{FILE_LOC}.update_json_file")
def test_save_to_group_empty_group_name(mock_update_json_file, mock_isfile):
    save_to_group("", ITEM_NAME)
    mock_isfile.assert_not_called()
    mock_update_json_file.assert_not_called()


@patch(f"{FILE_LOC}.isfile")
@patch(f"{FILE_LOC}.update_json_file")
def test_save_to_group_none_group_name(mock_update_json_file, mock_isfile):
    save_to_group(None, ITEM_NAME)
    mock_isfile.assert_not_called()
    mock_update_json_file.assert_not_called()


@patch(f"{FILE_LOC}.isfile")
@patch(f"{FILE_LOC}.get_file_contents")
@patch(f"{FILE_LOC}.update_json_file")
def test_save_to_group_existing_group(mock_update_json_file, mock_get_file_contents, mock_isfile):
    mock_isfile.return_value = True
    mock_get_file_contents.return_value = {"group name": GROUP_NAME, "items": ["existing item"]}
    save_to_group(GROUP_NAME, ITEM_NAME)
    mock_update_json_file.assert_called_once_with(
        {"group name": GROUP_NAME, "items": ["existing item", ITEM_NAME]},
        f"{EXPECTED_JSON_DIR}/groups/{GROUP_NAME}.json")

@pytest.mark.parametrize(
    ("from_db", "json_data", "expected_name"),
    [("DB Group", {}, "DB Group"),
     ("", {"group": "Json Group"}, "Json Group"),
     (None, {}, ""),
     ("DB Group", {"group": "Json Group"}, "Json Group")])
def test_get_updated_group_name(from_db, json_data, expected_name):
    assert get_updated_group_name(
        from_db, json_data) == expected_name

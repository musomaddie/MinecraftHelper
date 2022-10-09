from unittest.mock import call, patch

import pytest

from block_adder_flask.get_group_info import (
    ExistingGroupInfo, GroupInfoBuilder,
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
GROUP_MOCK_JSON_CONTENTS = {
    "group name": GROUP_NAME,
    "items": [ITEM_NAME, OTHER_ITEM_NAME]
}


@patch(f"{FILE_LOC}.ExistingGroupInfo.update_group_in_session")
def test_group_init_builder(mock_update_session):
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
    assert mock_update_session.called


@pytest.fixture
@patch(f"{FILE_LOC}.ExistingGroupInfo.update_group_in_session")
def existing_group_info(client):
    return ExistingGroupInfo(
        GROUP_NAME, ITEM_NAME, [OTHER_ITEM_NAME], True, MOCK_ITEM_CONTENTS, False
    )


@pytest.fixture
@patch(f"{FILE_LOC}.ExistingGroupInfo.update_group_in_session")
def existing_group_info_hidden():
    return ExistingGroupInfo(GROUP_NAME, ITEM_NAME, [], False, {}, False)


@patch(f"{FILE_LOC}.get_file_contents", return_value={"items": [ITEM_NAME, OTHER_ITEM_NAME]})
def test_get_group_item(mock_get_file_contents, existing_group_info):
    assert ExistingGroupInfo.get_group_items(GROUP_NAME, ITEM_NAME) == [
        OTHER_ITEM_NAME]
    mock_get_file_contents.assert_called_once_with(f"{EXPECTED_JSON_DIR}/groups/{GROUP_NAME}.json")


@patch(f"{FILE_LOC}.get_file_contents", return_value=GROUP_MOCK_JSON_CONTENTS)
@patch(f"{FILE_LOC}.ExistingGroupInfo.update_group_in_session")
def test_create_first_time(mock_update_session, mock_get_file_contents):
    result = ExistingGroupInfo.create_first_time(GROUP_NAME, ITEM_NAME)
    mock_get_file_contents.assert_has_calls(
        [call(f"{EXPECTED_JSON_DIR}/groups/{GROUP_NAME}.json"),
         call(f"{EXPECTED_JSON_DIR}/{OTHER_ITEM_NAME}.json")])
    assert result.group_name == GROUP_NAME
    assert result.current_item == ITEM_NAME
    assert result.other_items == [OTHER_ITEM_NAME]
    assert result.should_show
    assert not result.use_group_items


@patch(f"{FILE_LOC}.ExistingGroupInfo")
def test_create_from_dict(mock_existing_group_info):
    ExistingGroupInfo.create_from_dict(
        {"group_name": GROUP_NAME, "current_item": ITEM_NAME, "should_show": True,
         "other_items": [OTHER_ITEM_NAME], "other_item_info": MOCK_ITEM_CONTENTS,
         "use_group_items": False
         }
    )
    mock_existing_group_info.assert_called_once_with(
        GROUP_NAME, ITEM_NAME, [OTHER_ITEM_NAME], True, MOCK_ITEM_CONTENTS, False)


@pytest.mark.parametrize(
    ("should_show", "use_group_items", "expected"),
    [(False, False, []),
     (False, True, []),
     (True, False, []),
     (True, True, ["breaking_checkbox", "crafting_checkbox"])]
)
def test_get_obtaining_methods(existing_group_info, should_show, use_group_items, expected):
    existing_group_info.should_show = should_show
    existing_group_info.use_group_items = use_group_items
    assert existing_group_info.get_obtaining_methods() == expected


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

import copy
from unittest.mock import MagicMock, call, patch

import pytest

from block_adder_flask.get_group_info import (
    ExistingGroupInfo, GroupInfoBuilder,
    get_updated_group_name, remove_from_group, save_to_group)

ITEM_NAME = "Test Item"
OTHER_ITEM_NAME = "Test Other Item"
GROUP_NAME = "Test Group"
EXPECTED_JSON_DIR = "block_adder_flask/item_information"
FILE_LOC = "block_adder_flask.get_group_info"
# This will contain the max amount of information for each section so that there is less set up
# to do in each test.
MOCK_ITEM_CONTENTS = {
    "name": ITEM_NAME,
    "group": GROUP_NAME,
    "breaking":
        {"requires tool": True,
         "required tool": "pickaxe",
         "requires silk": True,
         "fastest tool": "pickaxe"},
    "breaking other": {
        "other block name": OTHER_ITEM_NAME,
        "likelihood of dropping": 32.5,
        "helped with fortune": True
    },
    "crafting": {
        "crafting slots": [
            OTHER_ITEM_NAME,
            "",
            "",
            OTHER_ITEM_NAME,
            OTHER_ITEM_NAME,
            "",
            OTHER_ITEM_NAME,
            OTHER_ITEM_NAME,
            OTHER_ITEM_NAME
        ],
        "num created": 4,
        "works with four by four": True,  # Set to true even though it shouldn't be in this case
        # to make testing easier.
        "requires exact positioning": True
    }
}
GROUP_MOCK_JSON_CONTENTS = {
    "group name": GROUP_NAME,
    "items": [ITEM_NAME, OTHER_ITEM_NAME]
}


@pytest.fixture
@patch(f"{FILE_LOC}.ExistingGroupInfo.update_group_in_session")
def existing_group_info(client):
    # Copying the mock item contents so any changes made to the dictionary in any tests are not
    # reflected for future tests.
    return ExistingGroupInfo(
        GROUP_NAME, ITEM_NAME, [OTHER_ITEM_NAME], True, copy.deepcopy(MOCK_ITEM_CONTENTS), True
    )


@pytest.fixture
@patch(f"{FILE_LOC}.ExistingGroupInfo.update_group_in_session")
def existing_group_info_hidden():
    return ExistingGroupInfo(GROUP_NAME, ITEM_NAME, [], False, {}, False)


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


####################################################################################################
#                                _HANDLE_MULTI_VALUE_OBT_METHOD                                    #
####################################################################################################
@pytest.mark.parametrize(
    ("get_file_contents_rv", "other_item_info", "expected_used_values_arguments"),
    [
        # 1 of 1
        ({}, {"this is": "a dict"}, [{"this is": "a dict"}, "next_button"]),
        # 1 of 2
        ({},
         [{"existing dict": 1}, {"existing dict": 2}],
         [{"existing dict": 1}, "another_button"]),
        # 2 of 2
        ({"method key": {"fake dictionary": 1}},
         [{"existing dict": 1}, {"existing dict": 2}],
         [{"existing dict": 2}, "next_button"]),
        # 2 of 3
        ({"method key": {"fake dictionary": 1}},
         [{"existing dict": 1}, {"existing dict": 2}, {"existing dict": 3}],
         [{"existing dict": 2}, "another_button"]),
        # 3 of 3
        ({"method key": [{"fake dictionary": 1}, {"fake dictionary": 2}]},
         [{"existing dict": 1}, {"existing dict": 2}, {"existing dict": 3}],
         [{"existing dict": 3}, "next_button"])
    ]
)
@patch(f"{FILE_LOC}.get_file_contents")
def test_handle_multi_value_obt_method(
        mock_get_file_contents,
        get_file_contents_rv,
        other_item_info,
        expected_used_values_arguments,
        existing_group_info):
    mock_get_file_contents.return_value = get_file_contents_rv
    existing_group_info.other_item_info["method key"] = other_item_info
    callback_mock = MagicMock()
    existing_group_info._handle_multi_value_obt_method("method key", callback_mock)
    callback_mock.assert_called_once_with(*expected_used_values_arguments)


####################################################################################################
#                                     GET_BREAKING_INFO                                            #
####################################################################################################

def test_get_breaking_info(existing_group_info):
    assert existing_group_info.get_breaking_info() == {
        "default_checked_ids": ["requires_tool_any", "requires_silk", "fastest_yes"],
        "select_default": {"fastest_tool": "pickaxe", "spec_tool_select": "pickaxe"},
        "button_to_click": "next_button"
    }


@pytest.mark.parametrize(
    ("should_show", "use_group_items", "other_item_info"),
    [(False, False, {}),
     (False, True, {}),
     (True, False, {}),
     (True, True, {})]
)
def test_get_breaking_info_empty_list(
        should_show, use_group_items, other_item_info, existing_group_info):
    existing_group_info.other_item_info = other_item_info
    existing_group_info.should_show = should_show
    existing_group_info.use_group_items = use_group_items
    assert existing_group_info.get_breaking_info() == []


def test_get_breaking_info_fastest_tool(existing_group_info):
    existing_group_info.other_item_info["breaking"]["fastest tool"] = "My Fastest Tool"
    result = existing_group_info.get_breaking_info()
    assert result["select_default"]["fastest_tool"] == "My Fastest Tool"
    assert "fastest_yes" in result["default_checked_ids"]


def test_get_breaking_info_fastest_tool_missing(existing_group_info):
    existing_group_info.other_item_info["breaking"] = {"requires tool": True, "requires silk": True}
    result = existing_group_info.get_breaking_info()
    assert len(result["default_checked_ids"]) == 2
    assert len(result["select_default"]) == 0


def test_get_breaking_info_required_tool(existing_group_info):
    existing_group_info.other_item_info["breaking"]["required tool"] = "MY TOOL"
    assert "MY TOOL" in existing_group_info.get_breaking_info()["select_default"][
        "spec_tool_select"]


def test_get_breaking_info_required_tool_missing(existing_group_info):
    existing_group_info.other_item_info["breaking"] = {"requires tool": True, "requires silk": True}
    assert len(existing_group_info.get_breaking_info()["select_default"]) == 0


@pytest.mark.parametrize(
    ("other_silk_value", "expected"),
    [(True, "requires_silk"),
     (False, "requires_silk_no")]
)
def test_get_breaking_info_silk_value(other_silk_value, expected, existing_group_info):
    existing_group_info.other_item_info["breaking"]["requires silk"] = other_silk_value
    assert expected in existing_group_info.get_breaking_info()["default_checked_ids"]


@pytest.mark.parametrize(
    ("other_tool_value", "expected"),
    [(True, "requires_tool_any"),
     (False, "requires_tool_no")]
)
def test_get_breaking_info_tool_value(other_tool_value, expected, existing_group_info):
    existing_group_info.other_item_info["breaking"]["requires tool"] = other_tool_value
    assert expected in existing_group_info.get_breaking_info()["default_checked_ids"]


####################################################################################################
#                              GET_BREAKING_OTHER_INFO                                             #
####################################################################################################

@pytest.mark.parametrize(
    ("should_show", "use_group_items", "other_item_info"),
    [(False, False, {}),
     (False, True, {}),
     (True, False, {}),
     (True, True, {})]
)
def test_get_breaking_other_info_empty_list(
        should_show, use_group_items, other_item_info, existing_group_info):
    existing_group_info.other_item_info = other_item_info
    existing_group_info.should_show = should_show
    existing_group_info.use_group_items = use_group_items
    assert existing_group_info.get_breaking_other_info() == []


def test_get_breaking_other_info_full_info(existing_group_info):
    assert existing_group_info.get_breaking_other_info() == {
        "percent_lhood_dropping": 32.5,
        "other_block": OTHER_ITEM_NAME,
        "should_fortune_checked": True
    }


def test_get_breaking_other_info_missing_fortune(existing_group_info):
    existing_group_info.other_item_info["breaking other"] = {
        "other block name": OTHER_ITEM_NAME,
        "helped with fortune": True
    }
    assert existing_group_info.get_breaking_other_info() == {
        "other_block": OTHER_ITEM_NAME,
        "should_fortune_checked": True
    }


####################################################################################################
#                              GET_CRAFTING_INFO                                                   #
####################################################################################################
@pytest.mark.parametrize(
    ("should_show", "use_group_items", "other_item_info"),
    [(False, False, {}),
     (False, True, {}),
     (True, False, {}),
     (True, True, {})]
)
def test_get_crafting_info_empty_list(
        should_show, use_group_items, other_item_info, existing_group_info):
    existing_group_info.other_item_info = other_item_info
    existing_group_info.should_show = should_show
    existing_group_info.use_group_items = use_group_items
    assert existing_group_info.get_crafting_info() == []


def test_get_crafting_info_full_info(existing_group_info):
    assert existing_group_info.get_crafting_info() == {
        "crafting_slots": {
            "cs1": OTHER_ITEM_NAME,
            "cs2": "",
            "cs3": "",
            "cs4": OTHER_ITEM_NAME,
            "cs5": OTHER_ITEM_NAME,
            "cs6": "",
            "cs7": OTHER_ITEM_NAME,
            "cs8": OTHER_ITEM_NAME,
            "cs9": OTHER_ITEM_NAME
        }, "n_created": 4,
        "default_selected": ["works_four_checkbox", "exact_pos_checkbox"],
        "button_to_click": "next_button"
    }


@patch(f"{FILE_LOC}.get_file_contents", return_value={"items": [ITEM_NAME, OTHER_ITEM_NAME]})
def test_get_group_item(mock_get_file_contents, existing_group_info):
    assert ExistingGroupInfo.get_group_items(GROUP_NAME, ITEM_NAME) == [
        OTHER_ITEM_NAME]
    mock_get_file_contents.assert_called_once_with(
        f"{EXPECTED_JSON_DIR}/groups/"
        f"{GROUP_NAME}.json")


@pytest.mark.parametrize(
    ("should_show", "use_group_items", "expected"),
    [(False, False, []),
     (False, True, []),
     (True, False, []),
     (True, True, ["breaking_checkbox", "breaking_other_checkbox", "crafting_checkbox"])]
)
def test_get_obtaining_methods(existing_group_info, should_show, use_group_items, expected):
    existing_group_info.should_show = should_show
    existing_group_info.use_group_items = use_group_items
    assert existing_group_info.get_obtaining_methods() == expected


@pytest.mark.parametrize(
    ("from_db", "json_data", "expected_name"),
    [("DB Group", {}, "DB Group"),
     ("", {"group": "Json Group"}, "Json Group"),
     (None, {}, ""),
     ("DB Group", {"group": "Json Group"}, "Json Group")])
def test_get_updated_group_name(from_db, json_data, expected_name):
    assert get_updated_group_name(
        from_db, json_data) == expected_name


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


####################################################################################################
#                                   REMOVE_FROM_GROUP                                              #
####################################################################################################

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
def test_remove_from_group_no_group(mock_get_file_contents):
    remove_from_group("", ITEM_NAME)
    mock_get_file_contents.assert_not_called()


@patch(f"{FILE_LOC}.get_file_contents")
def test_remove_from_group_none_group_name(mock_get_file_contents):
    remove_from_group(None, ITEM_NAME)
    mock_get_file_contents.assert_not_called()


@patch(f"{FILE_LOC}.get_file_contents")
@patch(f"{FILE_LOC}.os.remove")
def test_remove_from_group_only_item(mock_remove, mock_get_file_contents):
    mock_get_file_contents.return_value = {"group name": GROUP_NAME, "items": [ITEM_NAME]}
    remove_from_group(GROUP_NAME, ITEM_NAME)
    mock_remove.assert_called_once_with(f"{EXPECTED_JSON_DIR}/groups/{GROUP_NAME}.json")


####################################################################################################
#                                   SAVE_TO _GROUP                                                 #
####################################################################################################

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
@patch(f"{FILE_LOC}.get_file_contents")
@patch(f"{FILE_LOC}.update_json_file")
def test_save_to_group_existing_group(mock_update_json_file, mock_get_file_contents, mock_isfile):
    mock_isfile.return_value = True
    mock_get_file_contents.return_value = {"group name": GROUP_NAME, "items": ["existing item"]}
    save_to_group(GROUP_NAME, ITEM_NAME)
    mock_update_json_file.assert_called_once_with(
        {"group name": GROUP_NAME, "items": ["existing item", ITEM_NAME]},
        f"{EXPECTED_JSON_DIR}/groups/{GROUP_NAME}.json")


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
@patch(f"{FILE_LOC}.update_json_file")
def test_save_to_group_none_group_name(mock_update_json_file, mock_isfile):
    save_to_group(None, ITEM_NAME)
    mock_isfile.assert_not_called()
    mock_update_json_file.assert_not_called()


@patch(f"{FILE_LOC}.ExistingGroupInfo.update_group_in_session")
def test_use_values_button_clicked(mock_update_session, existing_group_info):
    existing_group_info.use_group_items = False
    assert not existing_group_info.use_group_items
    existing_group_info.use_values_button_clicked(True)
    assert existing_group_info.use_group_items
    assert mock_update_session.called

from unittest.mock import patch

import pytest

import populate_info.resources as r
from conftest import GROUP_3, ITEM_1, ITEM_2, GROUP_1, get_file_contents
from populate_info.group_utils import (
    add_to_group, get_group_breaking_info, get_group_categories, maybe_group_toggle_update_saved, should_show_group,
    write_group_data_to_json)

FILE_LOC = "populate_info.group_utils"


# #################################################################################################################### #
#  add_to_group                                                                                                        #
# #################################################################################################################### #
@patch(f"{FILE_LOC}.add_to_group_file")
def test_add_to_group_new_group(mock_add_to_file):
    add_to_group(GROUP_3, ITEM_1)
    mock_add_to_file.assert_called_once_with(GROUP_3, ITEM_1)


@patch(f"{FILE_LOC}.add_to_group_file")
def test_add_to_group_non_interesting_group_name(mock_add_to_file):
    add_to_group("", ITEM_1)
    assert not mock_add_to_file.called


# #################################################################################################################### #
#  should_show_group                                                                                                   #
# #################################################################################################################### #

@pytest.mark.parametrize("item_name", [ITEM_1, ITEM_2])
def test_should_show_group_true(client, group_file_with_2_items, item_name):
    with client.session_transaction() as session:
        session[r.CUR_ITEM_SK] = item_name
    assert should_show_group(group_file_with_2_items)


def test_should_show_group_false_no_other_items(client, group_file_with_1_item):
    with client.session_transaction() as session:
        session[r.CUR_ITEM_SK] = ITEM_1
    assert not should_show_group(group_file_with_1_item)


def test_should_show_group_false_poor_group_name():
    assert not should_show_group("")
    assert not should_show_group(None)


# #################################################################################################################### #
#  get group categories                                                                                                #
# #################################################################################################################### #
def test_get_group_categories_all_categories(group_file_all_categories):
    result = get_group_categories(group_file_all_categories)
    assert len(result) == 1
    assert "breaking" in result


def test_get_group_categories_noninteresting_group():
    assert get_group_categories("") == []


# #################################################################################################################### #
#  get group breaking info                                                                                             #
# #################################################################################################################### #
def test_get_group_breaking_info(group_file_all_categories):
    result = get_group_breaking_info(group_file_all_categories)
    assert "requires tool" in result
    assert result["requires tool"] == "any"
    assert "fastest tool" in result
    assert result["fastest tool"] == "Axe"
    assert "silk touch"
    assert not result["silk touch"]


def test_get_group_breaking_info_noninteresting_group_name():
    result = get_group_breaking_info("")
    assert result == []


# #################################################################################################################### #
#  maybe update button                                                                                                 #
# #################################################################################################################### #

@pytest.mark.parametrize("request_form", [{}, {"not what we want": "hehehe"}])
def test_maybe_group_toggle_update_false_not_included(request_form):
    assert not maybe_group_toggle_update_saved({}, request_form)


def test_maybe_group_toggle_update_true_dont_use():
    my_session = {}
    assert maybe_group_toggle_update_saved(my_session, {"update_use_group_values": "", "group_checkbox": ""})
    assert not my_session[r.USE_GROUP_VALUES_SK]


def test_maybe_group_toggle_update_true_use():
    my_session = {}
    assert maybe_group_toggle_update_saved(my_session, {"update_use_group_values": ""})
    assert my_session[r.USE_GROUP_VALUES_SK]


# #################################################################################################################### #
#  write group data to json                                                                                            #
# #################################################################################################################### #

def test_write_group_data_to_json(item_file_name_only):
    write_group_data_to_json(item_file_name_only, GROUP_1)
    result = get_file_contents(r.get_item_fn(item_file_name_only))
    assert r.GROUP_NAME_KEY in result
    assert result[r.GROUP_NAME_KEY] == GROUP_1


def test_write_group_data_to_json_not_interesting(item_file_name_only):
    write_group_data_to_json(item_file_name_only, "")
    result = get_file_contents(r.get_item_fn(item_file_name_only))
    assert r.GROUP_NAME_KEY not in result

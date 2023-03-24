import pytest

import populate_info.resources as r
from conftest import ITEM_1, ITEM_2
from populate_info.group_utils import get_group_breaking_info, get_group_categories, maybe_group_toggle_update_saved, \
    should_show_group


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


# #################################################################################################################### #
#  get group breaking info                                                                                             #
# #################################################################################################################### #
def test_get_group_breaking_info(group_file_all_categories):
    result = get_group_breaking_info(group_file_all_categories)
    assert "required tool" in result
    assert result["required tool"] == "any"
    assert "fastest tool" in result
    assert result["fastest tool"] == "Axe"
    assert "silk touch"
    assert not result["silk touch"]


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

import pytest

import populate_info.resources as r
from conftest import ITEM_1, ITEM_2
from populate_info.group_utils import should_show_group, get_group_categories


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

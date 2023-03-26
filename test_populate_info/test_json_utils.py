import json
from os import path

import pytest

import populate_info.resources as r
from conftest import GROUP_1, ITEM_1, ITEM_2, ITEM_3, get_file_contents, assert_dictionary_values
from populate_info import json_utils
from populate_info.json_utils import create_json_file, write_json_category_to_file


# #################################################################################################################### #
#  add to group file                                                                                                   #
# #################################################################################################################### #
def test_add_to_group_file_new_file():
    json_utils.add_to_group_file(GROUP_1, ITEM_1)

    assert path.exists(r.get_group_fn(GROUP_1))
    content = get_file_contents(r.get_group_fn(GROUP_1))

    assert r.GROUP_NAME_KEY in content
    assert content[r.GROUP_NAME_KEY] == GROUP_1

    assert r.GROUP_ITEMS_KEY in content
    assert len(content[r.GROUP_ITEMS_KEY]) == 1
    assert content[r.GROUP_ITEMS_KEY][0] == ITEM_1


@pytest.mark.parametrize("group_name", ("", None))
def test_add_to_group_file_poor_group_name(group_name):
    json_utils.add_to_group_file(group_name, ITEM_1)
    assert not path.exists(r.get_group_fn(""))


def test_add_to_group_file_existing_group(group_file_with_1_item):
    json_utils.add_to_group_file(group_file_with_1_item, ITEM_2)
    assert path.exists(r.get_group_fn(group_file_with_1_item))
    contents = get_file_contents(r.get_group_fn(group_file_with_1_item))

    assert r.GROUP_NAME_KEY in contents
    assert contents[r.GROUP_NAME_KEY] == group_file_with_1_item

    assert r.GROUP_ITEMS_KEY in contents
    assert len(contents[r.GROUP_ITEMS_KEY]) == 2
    assert contents[r.GROUP_ITEMS_KEY][1] == ITEM_2


# #################################################################################################################### #
#  create json file                                                                                                    #
# #################################################################################################################### #
def test_create_json_file():
    assert not path.exists(r.get_item_fn(ITEM_3))
    create_json_file(ITEM_3)
    assert path.exists(r.get_item_fn(ITEM_3))
    result = get_file_contents(r.get_item_fn(ITEM_3))
    assert_dictionary_values(result, [[r.ITEM_NAME_KEY, ITEM_3]])


# #################################################################################################################### #
#  get next block tests                                                                                                #
# #################################################################################################################### #
def test_get_next_item_first_item():
    assert json_utils.get_next_item() == ITEM_1


def test_get_next_item_has_items():
    with open(r.ADDED_ITEM_FN, "w") as f:
        json.dump({r.ITEM_LIST_KEY: [ITEM_1]}, f)
    assert json_utils.get_next_item() == ITEM_2


def test_get_next_item_no_items_left():
    with open(r.ADDED_ITEM_FN, "w") as f:
        json.dump({r.ITEM_LIST_KEY: [ITEM_1, ITEM_2, ITEM_3]}, f)
    assert json_utils.get_next_item() is None


# #################################################################################################################### #
#  remove from group file                                                                                              #
# #################################################################################################################### #
def test_remove_from_group_file_doesnt_exist():
    json_utils.remove_from_group_file(GROUP_1, ITEM_1)
    # Should run without problems.
    assert True


def test_remove_from_group_only_item(group_file_no_items):
    json_utils.add_to_group_file(GROUP_1, ITEM_1)
    json_utils.remove_from_group_file(GROUP_1, ITEM_1)
    result = get_file_contents(r.get_group_fn(GROUP_1))[r.ITEM_LIST_KEY]
    assert result == []


def test_remove_from_group_other_items(group_file_with_1_item):
    json_utils.add_to_group_file(GROUP_1, ITEM_2)
    json_utils.remove_from_group_file(GROUP_1, ITEM_2)
    result = get_file_contents(r.get_group_fn(GROUP_1))[r.ITEM_LIST_KEY]
    assert result == [ITEM_1]


def test_remove_from_group_without_item(group_file_with_1_item):
    original = get_file_contents(r.get_group_fn(GROUP_1))
    json_utils.remove_from_group_file(GROUP_1, ITEM_2)
    result = get_file_contents(r.get_group_fn(GROUP_1))
    assert result == original


# #################################################################################################################### #
#  write json category                                                                                                #
# #################################################################################################################### #
def test_write_json_category_to_file(item_file_name_only):
    cat_name = "testing info"
    category_info = {"key1": "value 1", "key2": "value 2"}
    write_json_category_to_file(item_file_name_only, cat_name, category_info)
    assert_dictionary_values(
        get_file_contents(r.get_item_fn(item_file_name_only)),
        [(r.ITEM_NAME_KEY, item_file_name_only),
         (cat_name, category_info)]
    )

# TODO - file not found.

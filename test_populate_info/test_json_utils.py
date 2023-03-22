import json
from os import path

import pytest

import populate_info.resources as r
from conftest import NEW_GROUP, TEST_ITEM, EXISTING_GROUP
from populate_info import json_utils


def _get_file_contents(filename: str) -> dict:
    with open(filename) as f:
        return json.load(f)


# ################################## add_to_group_file ################################
def test_add_to_group_file_new_file():
    json_utils.add_to_group_file(NEW_GROUP, TEST_ITEM)

    assert path.exists(r.get_group_fn(NEW_GROUP))
    content = _get_file_contents(r.get_group_fn(NEW_GROUP))

    assert r.GROUP_NAME_KEY in content
    assert content[r.GROUP_NAME_KEY] == NEW_GROUP

    assert r.GROUP_ITEMS_KEY in content
    assert len(content[r.GROUP_ITEMS_KEY]) == 1
    assert content[r.GROUP_ITEMS_KEY][0] == TEST_ITEM


@pytest.mark.parametrize("group_name", ("", None))
def test_add_to_group_file_poor_group_name(group_name):
    json_utils.add_to_group_file(group_name, TEST_ITEM)
    assert not path.exists(r.get_group_fn(""))


def test_add_to_group_file_existing_group():
    json_utils.add_to_group_file(EXISTING_GROUP, TEST_ITEM)
    assert path.exists(r.get_group_fn(EXISTING_GROUP))
    contents = _get_file_contents(r.get_group_fn(EXISTING_GROUP))

    assert r.GROUP_NAME_KEY in contents
    assert contents[r.GROUP_NAME_KEY] == EXISTING_GROUP

    assert r.GROUP_ITEMS_KEY in contents
    assert len(contents[r.GROUP_ITEMS_KEY]) == 2
    assert contents[r.GROUP_ITEMS_KEY][1] == TEST_ITEM


# ################################### get_next_block tests ##################################
def test_get_next_item_first_item():
    assert json_utils.get_next_item() == "A Item"


def test_get_next_item_has_items():
    with open(r.ADDED_ITEM_FN, "w") as f:
        json.dump({r.ITEM_LIST_KEY: ["A Item"]}, f)
    assert json_utils.get_next_item() == "Second Item"


def test_get_next_item_no_items_left():
    with open(r.ADDED_ITEM_FN, "w") as f:
        json.dump({r.ITEM_LIST_KEY: [
            "A Item",
            "Second Item",
            "Yet Another Item"]}, f)
    assert json_utils.get_next_item() is None

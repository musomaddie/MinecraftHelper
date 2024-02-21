""" tests for the group json parser. """
import json

import pytest

from populate_info.item_group.group_parser import KEY_GROUP_NAME, KEY_ITEM_LIST, GroupJsonParser

TEST_GROUP_NAME = "testing group"
TEST_GROUP_ITEM = "test item"

FAKE_ITEM_1 = "Item 1"
FAKE_ITEM_2 = "Item 2"
FAKE_ITEM_3 = "Item 3"


@pytest.fixture
def parser_group_all_categories():
    """ Creates a parser with a corresponding json file containing a group with all categories populated."""
    breaking_data = {
        # TODO revisit this content after full cleanup.
        "requires tool": "any",
        "fastest tool": "Axe",
        "silk touch": False
    }
    crafting_data = {
        "slots": {
            "1": FAKE_ITEM_1,
            "2": FAKE_ITEM_2,
            "3": FAKE_ITEM_3
        }
    }
    environment_changes_data = {"change": "description"}
    full_data = {
        KEY_GROUP_NAME: TEST_GROUP_NAME,
        KEY_ITEM_LIST: [TEST_GROUP_ITEM],
        "breaking": breaking_data,
        "crafting": crafting_data,
        "environment changes": environment_changes_data,
    }
    with open("populate_info/item_data/groups/testing_group.json", "w") as f:
        json.dump(full_data, f)

    return GroupJsonParser(TEST_GROUP_NAME)


@pytest.fixture
def parser_missing_corresponding_file():
    """ Returns a parser that's missing the """
    return GroupJsonParser("No file here")


class TestGetAllCategories:
    """ Tests for the get_all_categories method. """

    def test_all_categories(self, parser_group_all_categories):
        assert parser_group_all_categories.get_all_categories() == [
            "breaking", "crafting", "environment changes"
        ]

    def test_without_file(self, parser_missing_corresponding_file):
        assert parser_missing_corresponding_file.get_all_categories() == []


class TestGetAllItems:
    """ Tests for the get_all_items method. """

    def test_all_categories(self, parser_group_all_categories):
        assert parser_group_all_categories.get_all_items() == [TEST_GROUP_ITEM]

    def test_without_file(self, parser_missing_corresponding_file):
        assert parser_missing_corresponding_file.get_all_items() == []

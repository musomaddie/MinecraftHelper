""" Tests for the group class. """
import json
from os import path

import pytest

from conftest import get_file_contents
from populate_info.item_group import group_factory
from populate_info.item_group.group import Group
from populate_info.item_group.group_parser import KEY_GROUP_NAME, KEY_ITEM_LIST

FAKE_ITEM_1 = "Item 1"
FAKE_ITEM_2 = "Item 2"
FAKE_ITEM_3 = "Item 3"

TEST_GROUP_NAME = "testing group"
TEST_GROUP_ITEM = "test item"

EXISTING_GROUP_FILE = "populate_info/item_data/groups/testing_group.json"
NEW_GROUP_FILE = "populate_info/item_data/groups/missing_group.json"


@pytest.fixture
def group_all_categories() -> Group:
    """ Returns a group with all categories populated."""
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
        KEY_ITEM_LIST: [FAKE_ITEM_1, FAKE_ITEM_2],
        "breaking": breaking_data,
        "crafting": crafting_data,
        "environment changes": environment_changes_data,
    }
    # TODO replace the protected call with using the write method.
    with open("populate_info/item_data/groups/testing_group.json", "w") as f:
        json.dump(full_data, f)
    return group_factory.create(
        TEST_GROUP_NAME, TEST_GROUP_ITEM,
    )


@pytest.fixture
def group_non_interesting() -> Group:
    """ Returns a very boring group."""
    return group_factory.create(
        "", "missing group"
    )


@pytest.fixture(autouse=True)
def group_file_all_categories(group_all_categories):
    """ Creates a JSON file corresponding to a group with all categories. """


class TestShouldShowGroup:
    """ Tests for the should show group method. """

    def test_interesting_group(self, group_all_categories):
        assert group_all_categories.should_show_group()

    def test_non_interesting_group(self, group_non_interesting):
        assert not group_non_interesting.should_show_group()


class TestCategoriesHtmlIds:
    """ Tests for the categories_html_ids method."""

    def test_all_categories(self, group_all_categories, group_file_all_categories):
        result = group_all_categories.categories_html_ids()
        assert result == ["breaking-cbox", "crafting-cbox", "env-changes-cbox"]

    def test_hidden_group(self, group_non_interesting):
        assert group_non_interesting.categories_html_ids() == []


class TestCheckToggleSelected:
    """ Tests for the check_toggle_selected method. """

    @pytest.mark.parametrize("request_form", [{}, {"not what we want": "hehehe"}])
    def test_not_in_form_false(self, request_form, group_all_categories):
        previous_toggle_value = group_all_categories.use_group_values
        assert not group_all_categories.check_toggle_selected(request_form)
        assert previous_toggle_value == group_all_categories.use_group_values

    def test_in_form_with_update_request_true(self, group_non_interesting):
        assert group_non_interesting.check_toggle_selected(
            {"update-use-group-values": "", "group-checkbox": ""})
        assert group_non_interesting.use_group_values

    def test_in_form_no_update_requested_true(self, group_non_interesting):
        assert group_non_interesting.check_toggle_selected(
            {"update-use-group-values": ""})
        assert not group_non_interesting.use_group_values


class TestAddCurrentItemToJson:
    """ Tests for add_current_item_to_json"""

    def test_interesting_group(self, group_all_categories):
        group_all_categories.add_current_item_to_json()
        contents = get_file_contents(EXISTING_GROUP_FILE)
        assert contents.get("items") == [FAKE_ITEM_1, FAKE_ITEM_2, TEST_GROUP_ITEM]

    def test_new_file(self, group_non_interesting):
        group_non_interesting.add_current_item_to_json()
        # The group file should not actually exist.
        assert not path.exists(NEW_GROUP_FILE)

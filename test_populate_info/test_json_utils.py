import json
from os import path

import pytest

import populate_info.resources as r
from conftest import GROUP_1, ITEM_1, ITEM_2, ITEM_3, get_file_contents, assert_dictionary_values
from populate_info import json_utils
from populate_info.json_utils import create_json_file, write_json_category_to_file, get_current_category_info


class TestAddToGroupFile:
    def test_new_file(self):
        json_utils.add_to_group_file(GROUP_1, ITEM_1)

        assert path.exists(r.get_group_fn(GROUP_1))
        content = get_file_contents(r.get_group_fn(GROUP_1))

        assert r.GROUP_NAME_KEY in content
        assert content[r.GROUP_NAME_KEY] == GROUP_1

        assert r.GROUP_ITEMS_KEY in content
        assert len(content[r.GROUP_ITEMS_KEY]) == 1
        assert content[r.GROUP_ITEMS_KEY][0] == ITEM_1

    @pytest.mark.parametrize("group_name", ("", None))
    def test_poor_group_name(self, group_name):
        json_utils.add_to_group_file(group_name, ITEM_1)
        assert not path.exists(r.get_group_fn(""))

    def test_existing_group(self, group_file_with_1_item):
        json_utils.add_to_group_file(group_file_with_1_item, ITEM_2)
        assert path.exists(r.get_group_fn(group_file_with_1_item))
        contents = get_file_contents(r.get_group_fn(group_file_with_1_item))

        assert r.GROUP_NAME_KEY in contents
        assert contents[r.GROUP_NAME_KEY] == group_file_with_1_item

        assert r.GROUP_ITEMS_KEY in contents
        assert len(contents[r.GROUP_ITEMS_KEY]) == 2
        assert contents[r.GROUP_ITEMS_KEY][1] == ITEM_2


class TestCreateJsonFile:
    def test_happy(self):
        assert not path.exists(r.get_item_fn(ITEM_3))
        create_json_file(ITEM_3)
        assert path.exists(r.get_item_fn(ITEM_3))
        result = get_file_contents(r.get_item_fn(ITEM_3))
        assert_dictionary_values(result, [[r.ITEM_NAME_KEY, ITEM_3]])


class TestGetNextBlock:
    def test_get_next_item_first_item(self):
        assert json_utils.get_next_item() == ITEM_1

    def test_get_next_item_has_items(self):
        with open(r.ADDED_ITEM_FN, "w") as f:
            json.dump({r.ITEM_LIST_KEY: [ITEM_1]}, f)
        assert json_utils.get_next_item() == ITEM_2

    def test_get_next_item_no_items_left(self):
        with open(r.ADDED_ITEM_FN, "w") as f:
            json.dump({r.ITEM_LIST_KEY: [ITEM_1, ITEM_2, ITEM_3]}, f)
        assert json_utils.get_next_item() is None


class TestRemoveFromGroupFile:

    def test_doesnt_exist(self):
        json_utils.remove_from_group_file(GROUP_1, ITEM_1)
        # Should run without problems.
        assert True

    def test_only_item(self, group_file_no_items):
        json_utils.add_to_group_file(GROUP_1, ITEM_1)
        json_utils.remove_from_group_file(GROUP_1, ITEM_1)
        result = get_file_contents(r.get_group_fn(GROUP_1))[r.ITEM_LIST_KEY]
        assert result == []

    def test_other_items(self, group_file_with_1_item):
        json_utils.add_to_group_file(GROUP_1, ITEM_2)
        json_utils.remove_from_group_file(GROUP_1, ITEM_2)
        result = get_file_contents(r.get_group_fn(GROUP_1))[r.ITEM_LIST_KEY]
        assert result == [ITEM_1]

    def test_without_item(self, group_file_with_1_item):
        original = get_file_contents(r.get_group_fn(GROUP_1))
        json_utils.remove_from_group_file(GROUP_1, ITEM_2)
        result = get_file_contents(r.get_group_fn(GROUP_1))
        assert result == original


class TestWriteJsonCategoryToFile:

    def test_add_to_category_for_first_time(self, item_file_name_only):
        cat_name = "testing info"
        category_info = {"key 1": "value 1", "key 2": "value 2"}
        write_json_category_to_file(item_file_name_only, cat_name, category_info)
        assert_dictionary_values(
            get_file_contents(r.get_item_fn(item_file_name_only)),
            [(r.ITEM_NAME_KEY, item_file_name_only),
             (cat_name, category_info)]
        )

    def test_category_in_file_becomes_list(self, item_file_name_only):
        cat_name = "testing info"
        cat_info_1 = {"key 1": "value 1"}
        write_json_category_to_file(item_file_name_only, cat_name, cat_info_1)
        cat_info_2 = {"key 1 (2)": "value 1 (2)", "key 2": "value 2"}

        write_json_category_to_file(item_file_name_only, cat_name, cat_info_2)
        result = get_file_contents(r.get_item_fn(item_file_name_only))[cat_name]
        assert type(result) == list
        assert len(result) == 2
        assert_dictionary_values(result[0], [("key 1", "value 1")])
        assert_dictionary_values(result[1], [(key, value) for key, value in cat_info_2.items()])

    def test_category_in_file_3_times(self, item_file_name_only):
        cat_name = "testing info"
        cat_info_1 = {"k1": "v1"}
        cat_info_2 = {"k1": "v2"}
        cat_info_3 = {"k1": "v3"}
        write_json_category_to_file(item_file_name_only, cat_name, cat_info_1)
        write_json_category_to_file(item_file_name_only, cat_name, cat_info_2)
        write_json_category_to_file(item_file_name_only, cat_name, cat_info_3)

        result = get_file_contents(r.get_item_fn(item_file_name_only))[cat_name]
        assert type(result) == list
        assert len(result) == 3
        assert_dictionary_values(result[0], [(k, v) for k, v in cat_info_1.items()])
        assert_dictionary_values(result[1], [(k, v) for k, v in cat_info_2.items()])
        assert_dictionary_values(result[2], [(k, v) for k, v in cat_info_3.items()])


class TestGetCurrentCategoryInfo:
    def test_exists(self, item_file_name_only):
        cat_info = {"changes": ["change 1 description"]}
        write_json_category_to_file(
            item_file_name_only,
            "environment changes",
            cat_info
        )
        assert get_current_category_info(item_file_name_only, "environment changes") == cat_info

    def test_doesnt_exist(self, item_file_name_only):
        assert get_current_category_info(item_file_name_only, "environment changes") == {}

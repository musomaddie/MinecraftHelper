import copy
from unittest.mock import patch

import pytest

import populate_info.resources as r
from conftest import GROUP_1, GROUP_3, ITEM_1, ITEM_2, ITEM_3, assert_dictionary_values, get_file_contents
from populate_info.group_utils import (
    _maybe_generalise_category_info, _remove_shared_part, _replace_placeholder, add_to_group, get_group_breaking_info,
    get_group_categories,
    get_group_crafting_info, maybe_group_toggle_update_saved, should_show_group, write_group_name_to_item_json)

FILE_LOC = "populate_info.group_utils"


class TestAddToGroup:
    @patch(f"{FILE_LOC}.add_to_group_file")
    def test_new_group(self, mock_add_to_file):
        add_to_group(GROUP_3, ITEM_1)
        mock_add_to_file.assert_called_once_with(GROUP_3, ITEM_1)

    @patch(f"{FILE_LOC}.add_to_group_file")
    def test_non_interesting_group_name(self, mock_add_to_file):
        add_to_group("", ITEM_1)
        assert not mock_add_to_file.called


class TestGetGroupCategories:
    def test_all_categories(self, group_file_all_categories):
        result = get_group_categories(group_file_all_categories)
        assert len(result) == 3
        assert "breaking" in result
        assert "crafting" in result
        assert "environment changes" in result

    def test_noninteresting_group(self):
        assert get_group_categories("") == []


class TestGetGroupBreakingInfo:

    def test_simple(self, group_file_all_categories):
        result = get_group_breaking_info(group_file_all_categories, ITEM_1)
        assert "requires tool" in result
        assert result["requires tool"] == "any"
        assert "fastest tool" in result
        assert result["fastest tool"] == "Axe"
        assert "silk touch"
        assert not result["silk touch"]

    def test_noninteresting_group_name(self):
        result = get_group_breaking_info("", ITEM_1)
        assert result == {}


class TestGetGroupCraftingInfo:
    def test_simple(self, group_file_all_categories):
        result = get_group_crafting_info(group_file_all_categories, ITEM_1)
        assert_dictionary_values(
            result,
            [("slots", {"1": ITEM_1, "2": ITEM_2, "3": ITEM_3}),
             ("number created", 1),
             ("relative positioning", "strict"),
             ("works in smaller grid", False)])

    def test_noninteresting_group_name(self):
        result = get_group_crafting_info("", ITEM_1)
        assert result == {}


class TestMaybeGeneraliseCategoryInfo:
    def test_updates_one_matching_word(self):
        cat_info = {
            "slots":
                {"1": "Acacia Planks"},
            "number created": 2,
        }
        _maybe_generalise_category_info("Wooden Button", "Acacia Button", "crafting", cat_info)
        assert cat_info.get("slots").get("1") == "<PLACEHOLDER> Planks"

    def test_no_shared_words(self):
        cat_info = {
            "slots": {"1": "Planks"}, "number created": 2
        }
        old_cat_info = copy.deepcopy(cat_info)
        _maybe_generalise_category_info("Button", "Acacia", "crafting", cat_info)
        assert old_cat_info == cat_info

    def test_no_common_between_item_name_and_cat_info(self):
        cat_info = {
            "slots": {"1": "Planks"}, "number created": 2
        }
        old_cat_info = copy.deepcopy(cat_info)
        _maybe_generalise_category_info("Wooden Button", "Acacia Button", "crafting", cat_info)
        assert old_cat_info == cat_info

    def test_cat_key_not_interesting(self):
        cat_info = {"breaking": {"requires tool": "any", "silk touch": False, "fastest tool": "Pickaxe"}}
        old_cat_info = copy.deepcopy(cat_info)
        _maybe_generalise_category_info("Wooden Button", "Acacia Button", "breaking", cat_info)
        assert old_cat_info == cat_info


class TestMaybeUpdateButton:

    @pytest.mark.parametrize("request_form", [{}, {"not what we want": "hehehe"}])
    def test_false_not_included(self, request_form):
        assert not maybe_group_toggle_update_saved({}, request_form)

    def test_true_dont_use(self):
        my_session = {}
        assert maybe_group_toggle_update_saved(my_session, {"update_use_group_values": "", "group_checkbox": ""})
        assert not my_session[r.USE_GROUP_VALUES_SK]

    def test_true_use(self):
        my_session = {}
        assert maybe_group_toggle_update_saved(my_session, {"update_use_group_values": ""})
        assert my_session[r.USE_GROUP_VALUES_SK]


class TestRemoveSharedPart:
    def test_shares_word_one(self):
        assert "Different" == _remove_shared_part("Different Shared", "XXXXXX Shared")

    def test_shares_word_two_different(self):
        assert "Im Different" == _remove_shared_part("Im Shared Different", "Shared")

    def test_shares_two_words_one_different(self):
        assert "Different" == _remove_shared_part("Im Different Shared", "Im Shared")

    def test_totally_shared_raises_exception(self):
        with pytest.raises(ValueError):
            _remove_shared_part("Totally Identical", "Totally Identical")


class TestReplacePlaceholder:
    def test_breaking_call(self):
        breaking_dict = {"requires tool": "any", "silk touch": False, "fastest tool": "Pickaxe"}
        old_breaking_dict = copy.deepcopy(breaking_dict)
        _replace_placeholder("Existing", breaking_dict)
        assert old_breaking_dict == breaking_dict

    def test_crafting_call(self):
        crafting_dict = {"slots": {1: "<PLACEHOLDER> Planks", "3": "Anvil"}, "number created": 2}
        _replace_placeholder("Existing", crafting_dict)
        assert crafting_dict == {"slots": {1: "Existing Planks", "3": "Anvil"}, "number created": 2}


class TestShouldShowGroup:
    @pytest.mark.parametrize("item_name", [ITEM_1, ITEM_2])
    def test_true(self, client, group_file_with_2_items, item_name):
        with client.session_transaction() as session:
            session[r.CUR_ITEM_SK] = item_name
        assert should_show_group(group_file_with_2_items)

    def test_false_no_other_items(self, client, group_file_with_1_item):
        with client.session_transaction() as session:
            session[r.CUR_ITEM_SK] = ITEM_1
        assert not should_show_group(group_file_with_1_item)

    def test_should_show_group_false_poor_group_name(self):
        assert not should_show_group("")
        assert not should_show_group(None)


class TestWriteGroupDataToJson:

    def test_simple(self, item_file_name_only):
        write_group_name_to_item_json(item_file_name_only, GROUP_1)
        result = get_file_contents(r.get_item_fn(item_file_name_only))
        assert r.GROUP_NAME_KEY in result
        assert result[r.GROUP_NAME_KEY] == GROUP_1

    def test_not_interesting(self, item_file_name_only):
        write_group_name_to_item_json(item_file_name_only, "")
        result = get_file_contents(r.get_item_fn(item_file_name_only))
        assert r.GROUP_NAME_KEY not in result


class TestMaybeWriteCategoryToGroup:
    def test_maybe_write_category_to_group_happy(self):
        assert False

    def test_maybe_write_category_to_group_noninteresting_name(self):
        assert False

    def test_maybe_write_category_to_group_already_in_group(self):
        assert False

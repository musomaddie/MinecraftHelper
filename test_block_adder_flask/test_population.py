import json
from unittest.mock import call, patch

import pytest
from _pytest.fixtures import fixture

import block_adder_flask.manual_population as pop

ITEM_NAME = "Test Item"
GROUP_NAME = "Test Group"

FILE_LOC = "block_adder_flask.manual_population"
EXPECTED_JSON_DIR = "block_adder_flask/item_information"
REMAINING_ITEMS = "['breaking']"


@fixture
def tmp_json_file_no_items(tmpdir):
    filename = tmpdir.join("test.json")
    with open(filename, "w") as f:
        json.dump({"items": []}, f)
    return filename


def test_update_json_file(tmpdir):
    file = tmpdir.join("test.json")
    pop._update_json_file({"Testing": True}, file)
    with open(file) as f:
        result = json.load(f)
    assert result["Testing"]


def test_get_all_json_files_no_files(tmp_json_file_no_items):
    assert len(pop._get_all_items_json_file(tmp_json_file_no_items)) == 0


def test_get_all_json_files_with_data(tmpdir):
    file = tmpdir.join("testing_all_items.json")
    with open(file, "w") as f:
        json.dump({"items": ["T1"]}, f)
    result = pop._get_all_items_json_file(file)
    assert len(result) == 1
    assert result[0] == "T1"


def test_add_to_item_list(tmp_json_file_no_items):
    pop._add_to_item_list(ITEM_NAME, tmp_json_file_no_items)
    with open(tmp_json_file_no_items) as f:
        created_json = json.load(f)
        assert len(created_json["items"]) == 1
        assert created_json["items"][0] == ITEM_NAME


@patch(f"{FILE_LOC}.open")
@patch(f"{FILE_LOC}.json.load")
@patch(f"{FILE_LOC}._update_json_file")
def test_add_to_item_list_already_present(mock_update_json_file, mock_json_load, mock_open):
    mock_json_load.return_value = {"items": [ITEM_NAME]}
    pop._add_to_item_list(ITEM_NAME)
    mock_update_json_file.assert_called_once_with(
        {"items": [ITEM_NAME]}, f"{EXPECTED_JSON_DIR}/item_list.json")


@patch(f"{FILE_LOC}.isfile")
@patch(f"{FILE_LOC}._update_json_file")
def test_save_to_group_new_group(mock_update_json_file, mock_isfile):
    mock_isfile.return_value = False
    pop._save_to_group(GROUP_NAME, ITEM_NAME)
    mock_update_json_file.assert_called_once_with(
        {"group name": GROUP_NAME, "items": [ITEM_NAME]},
        f"{EXPECTED_JSON_DIR}/groups/{GROUP_NAME}.json"
    )


@patch(f"{FILE_LOC}.isfile")
@patch(f"{FILE_LOC}._get_file_contents")
@patch(f"{FILE_LOC}._update_json_file")
def test_save_to_group_already_in_group(mock_update_json_file, mock_get_file_contents, mock_isfile):
    mock_isfile.return_value = True
    mock_get_file_contents.return_value = {"group name": GROUP_NAME, "items": [ITEM_NAME]}
    pop._save_to_group(GROUP_NAME, ITEM_NAME)
    mock_update_json_file.assert_not_called()


@patch(f"{FILE_LOC}.isfile")
@patch(f"{FILE_LOC}._update_json_file")
def test_save_to_group_empty_group_name(mock_update_json_file, mock_isfile):
    pop._save_to_group("", ITEM_NAME)
    mock_isfile.assert_not_called()
    mock_update_json_file.assert_not_called()


@patch(f"{FILE_LOC}.isfile")
@patch(f"{FILE_LOC}._update_json_file")
def test_save_to_group_none_group_name(mock_update_json_file, mock_isfile):
    pop._save_to_group(None, ITEM_NAME)
    mock_isfile.assert_not_called()
    mock_update_json_file.assert_not_called()


@patch(f"{FILE_LOC}.isfile")
@patch(f"{FILE_LOC}._get_file_contents")
@patch(f"{FILE_LOC}._update_json_file")
def test_save_to_group_existing_group(mock_update_json_file, mock_get_file_contents, mock_isfile):
    mock_isfile.return_value = True
    mock_get_file_contents.return_value = {"group name": GROUP_NAME, "items": ["existing item"]}
    pop._save_to_group(GROUP_NAME, ITEM_NAME)
    mock_update_json_file.assert_called_once_with(
        {"group name": GROUP_NAME, "items": ["existing item", ITEM_NAME]},
        f"{EXPECTED_JSON_DIR}/groups/{GROUP_NAME}.json")


@patch(f"{FILE_LOC}._get_file_contents")
@patch(f"{FILE_LOC}._update_json_file")
def test_remove_from_group(mock_update_json_file, mock_get_file_contents):
    mock_get_file_contents.return_value = {
        "group name": GROUP_NAME, "items": ["Existing Item", ITEM_NAME]}
    pop._remove_from_group(GROUP_NAME, ITEM_NAME)
    mock_update_json_file.assert_called_once_with(
        {"group name": GROUP_NAME, "items": ["Existing Item"]},
        f"{EXPECTED_JSON_DIR}/groups/{GROUP_NAME}.json")


@patch(f"{FILE_LOC}._get_file_contents")
@patch(f"{FILE_LOC}.os.remove")
def test_remove_from_group_only_item(mock_remove, mock_get_file_contents):
    mock_get_file_contents.return_value = {"group name": GROUP_NAME, "items": [ITEM_NAME]}
    pop._remove_from_group(GROUP_NAME, ITEM_NAME)
    mock_remove.assert_called_once_with(f"{EXPECTED_JSON_DIR}/groups/{GROUP_NAME}.json")


@patch(f"{FILE_LOC}._get_file_contents")
def test_remove_from_group_no_group(mock_get_file_contents):
    pop._remove_from_group("", ITEM_NAME)
    mock_get_file_contents.assert_not_called()


@patch(f"{FILE_LOC}._get_file_contents")
def test_remove_from_group_none_group_name(mock_get_file_contents):
    pop._remove_from_group(None, ITEM_NAME)
    mock_get_file_contents.assert_not_called()


@pytest.mark.parametrize(
    ("from_db", "json_data", "expected_name"),
    [("DB Group", {}, "DB Group"),
     ("", {"group": "Json Group"}, "Json Group"),
     (None, {}, ""),
     ("DB Group", {"group": "Json Group"}, "Json Group")])
def test_get_updated_group_name(from_db, json_data, expected_name):
    assert pop._get_updated_group_name(from_db, json_data) == expected_name


@patch(f"{FILE_LOC}._update_json_file")
@patch(f"{FILE_LOC}._get_file_contents")
def test_append_json(mock_get_file_contents, mock_update_json_file, tmp_json_file_no_items):
    mock_get_file_contents.return_value = {"name": ITEM_NAME}
    pop._append_json_file(
        "test key", [("item 1", 45), ("item 2", True)], tmp_json_file_no_items)
    mock_update_json_file.assert_called_once_with(
        {"name": ITEM_NAME, "test key": {"item 1": 45, "item 2": True}}, tmp_json_file_no_items)


@patch(f"{FILE_LOC}._update_json_file")
@patch(f"{FILE_LOC}._get_file_contents")
def test_append_json_key_exists(
        mock_get_file_contents, mock_update_json_file, tmp_json_file_no_items):
    mock_get_file_contents.return_value = {
        "name": ITEM_NAME, "new key": {"item 1": "45", "item 2": 45}}
    pop._append_json_file(
        "new key",
        [("item 1a", "thing"), ("item 2a", "thing2")],
        tmp_json_file_no_items)
    mock_update_json_file.assert_called_once_with(
        {"name": ITEM_NAME, "new key":
            [{"item 1": "45", "item 2": 45}, {"item 1a": "thing", "item 2a": "thing2"}]},
        tmp_json_file_no_items
    )


@patch(f"{FILE_LOC}._update_json_file")
@patch(f"{FILE_LOC}._get_file_contents")
def test_append_json_condition_false(
        mock_get_file_contents, mock_update_json_file, tmp_json_file_no_items):
    mock_get_file_contents.return_value = {"name": ITEM_NAME}
    pop._append_json_file(
        "test key", [("item 1", "no condition"), ("item 2", "true condition", True),
                     ("item 3", "false condition", False)], tmp_json_file_no_items)
    mock_update_json_file.assert_called_once_with(
        {"name": ITEM_NAME, "test key":
            {"item 1": "no condition", "item 2": "true condition"}},
        tmp_json_file_no_items)


# ##################################################################################################
#                            item                                                                  #
# ##################################################################################################

@patch(f"{FILE_LOC}.join")
@patch(f"{FILE_LOC}.isfile")
@patch(f"{FILE_LOC}._get_file_contents")
@patch(f"{FILE_LOC}._add_to_item_list")
@patch(f"{FILE_LOC}.get_group")
@patch(f"{FILE_LOC}._save_to_group")
def test_add_item_get_file_exists_with_mocks(
        mock_save_to_group,
        mock_get_group,
        mock_add_to_item_list,
        mock_get_file_contents,
        mock_isfile,
        mock_join,
        client):
    # if isfile(join(JSON_DIR, item_file_name)):
    #     # TODO: rewrite to use reading helper
    #     existing_json_data = _get_file_contents(item_file_name_full)
    #     _add_to_item_list(item_name)
    mock_isfile.return_value = True
    mock_get_group.return_value = "Testing Group"
    response = client.get(f"/add_item/{ITEM_NAME}")
    assert response.status_code == 200
    mock_save_to_group.assert_called_once_with("Testing Group", ITEM_NAME)
    mock_join.assert_called_once_with("block_adder_flask/item_information", "Test Item.json")
    mock_isfile.assert_called_once()
    mock_get_file_contents.assert_called_once_with(f"{EXPECTED_JSON_DIR}/{ITEM_NAME}.json")
    mock_add_to_item_list.assert_called_once_with(ITEM_NAME)


@patch(f"{FILE_LOC}.join")
@patch(f"{FILE_LOC}.isfile")
@patch(f"{FILE_LOC}._update_json_file")
@patch(f"{FILE_LOC}.get_group")
@patch(f"{FILE_LOC}._save_to_group")
def test_add_item_get_doesnt_already_exist_with_mocks(
        mock_save_to_group, mock_get_group, mock_update_json_file, mock_isfile, mock_join,
        app, client):
    mock_isfile.return_value = False
    mock_get_group.return_value = "Testing Group"
    response = client.get(f"/add_item/{ITEM_NAME}")
    assert response.status_code == 200
    mock_save_to_group.assert_called_once_with("Testing Group", ITEM_NAME)
    mock_join.assert_called_once_with("block_adder_flask/item_information", "Test Item.json")
    mock_isfile.assert_called_once()
    mock_update_json_file.assert_called_once_with(
        {"name": ITEM_NAME}, f"{EXPECTED_JSON_DIR}/{ITEM_NAME}.json")


@patch(f"{FILE_LOC}.isfile")
@patch(f"{FILE_LOC}.get_group")
@patch(f"{FILE_LOC}._get_updated_group_name")
@patch(f"{FILE_LOC}._update_json_file")
@patch(f"{FILE_LOC}.url_for")
@patch(f"{FILE_LOC}.redirect")
@patch(f"{FILE_LOC}._save_to_group")
@patch(f"{FILE_LOC}._remove_from_group")
def test_add_item_update_group(
        mock_remove_from_group, mock_save_to_group, mock_redirect, mock_url_for,
        mock_update_file, mock_get_group_name, mock_get_group, mock_isfile, client):
    mock_isfile.return_value = False
    response = client.post(
        f"/add_item/{ITEM_NAME}",
        data={"update_group": True, "group_name_replacement": "New Group"})
    assert response.status_code == 200
    mock_remove_from_group.assert_called_once_with(mock_get_group_name.return_value, ITEM_NAME)
    mock_save_to_group.assert_called_once_with(mock_get_group_name.return_value, ITEM_NAME)
    mock_get_group.assert_called_once_with(ITEM_NAME)
    mock_update_file.assert_has_calls(
        [call(
            {"name": "Test Item", "group": "New Group"},
            f"{EXPECTED_JSON_DIR}/{ITEM_NAME}.json"),
            call(
                {"name": "Test Item", "group": "New Group"},
                f"{EXPECTED_JSON_DIR}/{ITEM_NAME}.json")
        ])
    mock_url_for.assert_called_once_with("add.item", item_name=ITEM_NAME)
    mock_redirect.assert_called_once()


@patch(f"{FILE_LOC}.join")
@patch(f"{FILE_LOC}._get_file_contents")
@patch(f"{FILE_LOC}._add_to_item_list")
@patch(f"{FILE_LOC}.isfile")
@patch(f"{FILE_LOC}.open")
@patch(f"{FILE_LOC}.get_group")
@patch(f"{FILE_LOC}._get_updated_group_name")
@patch(f"{FILE_LOC}._update_json_file")
@patch(f"{FILE_LOC}.move_next_page")
def test_add_item_post(
        mock_move_next_page, mock_update_json_file, mock_get_updated_group_name, mock_get_group,
        mock_open, mock_isfile, mock_add_to_item_list, mock_file_contents, mock_join, client):
    mock_isfile = False
    response = client.post(
        f"/add_item/{ITEM_NAME}",
        data={"trading": "", "nat_gen": "", "breaking": "", "fishing": "", "nat_biome": "",
              "crafting": "", "nat_struct": ""})
    assert response.status_code == 200
    mock_move_next_page.assert_called_once_with(
        ITEM_NAME,
        ["add.breaking", "add.crafting", "add.fishing", "add.trading", "add.natural_generation",
         "add.natural_generation_biome", "add.natural_gen_structure"])


# ##################################################################################################
#                            breaking                                                              #
# ##################################################################################################

@pytest.mark.parametrize(
    ("tool_form_value", "specific_tool", "silk_form_value", "fastest_tool"),
    [("tool_no", "", "silk_no", ""),
     ("tool_yes", "", "silk_no", ""),
     ("tool_specific", "pickaxe", "silk_no", ""),
     ("tool_no", "", "silk_no", "axe"),
     ("tool_yes", "", "silk_no", "axe"),
     ("tool_specific", "pickaxe", "silk_no", "axe"),
     ("tool_no", "", "silk_yes", ""),
     ("tool_yes", "", "silk_yes", ""),
     ("tool_specific", "pickaxe", "silk_yes", ""),
     ("tool_no", "", "silk_yes", "axe"),
     ("tool_yes", "", "silk_yes", "axe"),
     ("tool_specific", "pickaxe", "silk_yes", "axe")])
@patch(f"{FILE_LOC}._append_json_file")
@patch(f"{FILE_LOC}.flash")
@patch(f"{FILE_LOC}.url_for")
@patch(f"{FILE_LOC}.redirect")
def test_breaking(
        mock_redirect, mock_url_for, mock_flash, mock_append_json_file,
        tool_form_value, specific_tool, silk_form_value, fastest_tool, client):
    form_data = {"requires_tool": tool_form_value,
                 "specific_tool": specific_tool,
                 "requires_silk": silk_form_value,
                 "fastest_specific_tool": fastest_tool}
    if fastest_tool != "":
        form_data["fastest_tool"] = ""
    response = client.post(f"/add_breaking/{ITEM_NAME}/{REMAINING_ITEMS}", data=form_data)
    assert response.status_code == 200
    mock_append_json_file.assert_called_once_with(
        "breaking", [
            ("requires tool", tool_form_value != "tool_no"),
            ("required tool", specific_tool, specific_tool != ""),
            ("requires silk", silk_form_value != "silk_no"),
            ("fastest tool", fastest_tool, fastest_tool != "")],
        f"{EXPECTED_JSON_DIR}/{ITEM_NAME}.json"
    )
    mock_flash.assert_called_once()
    mock_redirect.assert_called_once()
    mock_url_for.assert_called_once_with(
        "add.breaking", item_name=ITEM_NAME, remaining_items=REMAINING_ITEMS)


@patch(f"{FILE_LOC}._append_json_file")
@patch(f"{FILE_LOC}.flash")
@patch(f"{FILE_LOC}.url_for")
@patch(f"{FILE_LOC}.redirect")
def test_breaking_other(mock_redirect, mock_url_for, mock_flash, mock_append_json_file, client):
    response = client.post(
        f"/add_breaking_other/{ITEM_NAME}/{REMAINING_ITEMS}",
        data={"other_block": "Other Block", "percent_dropping": 10.12, "fortune": ""})
    assert response.status_code == 200
    mock_append_json_file.assert_called_once_with(
        "breaking other", [
            ("other block name", "Other Block"),
            ("likelihood of dropping", 10.12, True),
            ("helped with fortune", True)],
        f"{EXPECTED_JSON_DIR}/{ITEM_NAME}.json")


@patch(f"{FILE_LOC}._append_json_file")
@patch(f"{FILE_LOC}.flash")
@patch(f"{FILE_LOC}.move_next_page")
def test_breaking_next(mock_move_next_page, mock_flash, mock_append_json_file, client):
    response = client.post(
        f"/add_breaking/{ITEM_NAME}/{REMAINING_ITEMS}",
        data={"requires_tool": "tool_no", "requires_silk": "silk_no",
              "specific_tool": "", "fastest_specific_tool": "", "next": ""})
    assert response.status_code == 200
    mock_append_json_file.assert_called_once_with(
        "breaking",
        [("requires tool", False), ("required tool", "", False),
         ("requires silk", False), ("fastest tool", "", False)],
        f"{EXPECTED_JSON_DIR}/{ITEM_NAME}.json")
    mock_flash.assert_called_once()
    mock_move_next_page.assert_called_once_with(ITEM_NAME, REMAINING_ITEMS)


# ##################################################################################################
#                            crafting                                                              #
# ##################################################################################################
@patch(f"{FILE_LOC}._append_json_file")
@patch(f"{FILE_LOC}.flash")
@patch(f"{FILE_LOC}.redirect")
@patch(f"{FILE_LOC}.url_for")
def test_crafting(mock_url_for, mock_redirect, mock_flash, mock_append_json_file, client):
    form_data = {
        "cs1": "Item 1", "cs2": "Item 2", "cs3": "Item 3", "cs4": "Item 4", "cs5": "Item 5",
        "cs6": "Item 6", "cs7": "Item 7", "cs8": "Item 8", "cs9": "Item 9",
        "n_created": 1, "works_four": "", "exact_positioning": ""
    }
    expected_data = [
        ("crafting slots",
         ["Item 1", "Item 2", "Item 3", "Item 4", "Item 5", "Item 6", "Item 7", "Item 8",
          "Item 9"]),
        ("num created", 1),
        ("works with four by four", True),
        ("requires exact positioning", True)]
    response = client.post(f"/add_crafting/{ITEM_NAME}/{REMAINING_ITEMS}", data=form_data)
    assert response.status_code == 200
    mock_append_json_file.assert_called_once_with(
        "crafting", expected_data, f"{EXPECTED_JSON_DIR}/{ITEM_NAME}.json")
    mock_flash.assert_called_once()
    mock_redirect.assert_called_once()
    mock_url_for.assert_called_once_with(
        "add.crafting", item_name=ITEM_NAME, remaining_items=REMAINING_ITEMS)


@patch(f"{FILE_LOC}._append_json_file")
@patch(f"{FILE_LOC}.flash")
@patch(f"{FILE_LOC}.move_next_page")
def test_crafting_move_next(mock_move_next_page, mock_flash, mock_append_json, client):
    # Also testing with a not full crafting grid and without some booleans
    form_data = {
        "cs1": "Item 1", "cs3": "Item 2", "cs4": "Item 3", "cs5": "Item 4",
        "n_created": "1", "exact_positioning": "", "next": ""
    }
    expected_data = [
        ("crafting slots", ["Item 1", "", "Item 2", "Item 3", "Item 4", "", "", "", ""]),
        ("num created", 1),
        ("works with four by four", False),
        ("requires exact positioning", True)]
    response = client.post(f"/add_crafting/{ITEM_NAME}/{REMAINING_ITEMS}", data=form_data)
    assert response.status_code == 200
    mock_append_json.assert_called_once_with(
        "crafting", expected_data, f"{EXPECTED_JSON_DIR}/{ITEM_NAME}.json")
    mock_flash.assert_called_once()
    mock_move_next_page.assert_called_once_with(ITEM_NAME, REMAINING_ITEMS)


# ##################################################################################################
#                            fishing                                                               #
# ##################################################################################################
@patch(f"{FILE_LOC}._append_json_file")
@patch(f"{FILE_LOC}.flash")
@patch(f"{FILE_LOC}.move_next_page")
def test_fishing(mock_move_next_page, mock_flash, mock_append_json_file, client):
    response = client.post(
        f"/add_fishing/{ITEM_NAME}/{REMAINING_ITEMS}", data={"item_level": "Treasure"})
    assert response.status_code == 200
    mock_append_json_file.assert_called_once_with(
        "fishing", [("treasure type", "Treasure")], f"{EXPECTED_JSON_DIR}/{ITEM_NAME}.json")
    mock_flash.assert_called_once()
    mock_move_next_page.assert_called_once_with(ITEM_NAME, REMAINING_ITEMS)


# ##################################################################################################
#                            chest generation                                                      #
# ##################################################################################################

@pytest.mark.parametrize(
    ("has_container", "expected_container", "has_chance", "expected_chance"),
    [(True, "Container 1", True, 50),
     (True, "Container 1", False, 100),
     (False, "", True, 50),
     (False, "", False, 100)]
)
@patch(f"{FILE_LOC}._append_json_file")
@patch(f"{FILE_LOC}.flash")
@patch(f"{FILE_LOC}.url_for")
@patch(f"{FILE_LOC}.redirect")
def test_natural_generation(
        mock_redirect, mock_url_for, mock_flash, mock_append_json_file,
        has_container, expected_container, has_chance, expected_chance, client):
    form_data = {"structure": "Structure 1", "quantity_fd": 1}
    if has_container:
        form_data["container"] = expected_container
    if has_chance:
        form_data["chance"] = expected_chance

    response = client.post(f"/add_natural_generation/{ITEM_NAME}/{REMAINING_ITEMS}", data=form_data)
    assert response.status_code == 200
    mock_append_json_file.assert_called_once_with(
        "generated in chests",
        [("structure", "Structure 1"),
         ("container", expected_container, has_container),
         ("quantity", 1),
         ("chance", expected_chance, has_chance)],
        f"{EXPECTED_JSON_DIR}/{ITEM_NAME}.json")
    mock_flash.assert_called_once()
    mock_url_for.assert_called_once_with(
        "add.natural_generation", item_name=ITEM_NAME, remaining_items=REMAINING_ITEMS)
    mock_redirect.assert_called_once()


@patch(f"{FILE_LOC}._append_json_file")
@patch(f"{FILE_LOC}.flash")
@patch(f"{FILE_LOC}.move_next_page")
def test_natural_generation_move_next(
        mock_move_next_page, mock_flash, mock_append_json_file, client):
    response = client.post(
        f"/add_natural_generation/{ITEM_NAME}/{REMAINING_ITEMS}",
        data={"structure": "Structure 1", "quantity_fd": 2, "next": ""})
    assert response.status_code == 200
    mock_append_json_file.assert_called_once_with(
        "generated in chests",
        [("structure", "Structure 1"), ("container", "", False),
         ("quantity", 2), ("chance", 100, False)],
        f"{EXPECTED_JSON_DIR}/{ITEM_NAME}.json")
    mock_flash.assert_called_once()
    mock_move_next_page.assert_called_once_with(ITEM_NAME, REMAINING_ITEMS)


# ##################################################################################################
#                            biome generation                                                      #
# ##################################################################################################

@patch(f"{FILE_LOC}._append_json_file")
@patch(f"{FILE_LOC}.flash")
@patch(f"{FILE_LOC}.url_for")
@patch(f"{FILE_LOC}.redirect")
def test_natural_generation_biome(
        mock_redirect, mock_url_for, mock_flash, mock_append_json_file, client):
    response = client.post(
        f"/add_natural_biome/{ITEM_NAME}/{REMAINING_ITEMS}", data={"biome": "Test Biome"})
    assert response.status_code == 200
    mock_append_json_file.assert_called_once_with(
        "generated in biome", [("biome name", "Test Biome")],
        f"{EXPECTED_JSON_DIR}/{ITEM_NAME}.json")
    mock_flash.assert_called_once()
    mock_url_for.assert_called_once_with(
        "add.natural_generation_biome",
        item_name=ITEM_NAME, remaining_items=REMAINING_ITEMS)
    mock_redirect.assert_called_once()


@patch(f"{FILE_LOC}._append_json_file")
@patch(f"{FILE_LOC}.flash")
@patch(f"{FILE_LOC}.move_next_page")
def test_natural_generation_biome_next(
        mock_move_next_page, mock_flash, mock_append_json_file, client):
    response = client.post(
        f"/add_natural_biome/{ITEM_NAME}/{REMAINING_ITEMS}",
        data={"biome": "Test Biome", "next": ""})
    assert response.status_code == 200
    mock_append_json_file.assert_called_once()
    mock_flash.assert_called_once()
    mock_move_next_page.assert_called_once_with(ITEM_NAME, REMAINING_ITEMS)


# ##################################################################################################
#                            natural gen structure                                                 #
# ##################################################################################################

@patch(f"{FILE_LOC}._append_json_file")
@patch(f"{FILE_LOC}.flash")
@patch(f"{FILE_LOC}.redirect")
@patch(f"{FILE_LOC}.url_for")
def test_natural_gen_structure(
        mock_url_for, mock_redirect, mock_flash, mock_append_json_file, client):
    response = client.post(
        f"/add_natural_gen_structure/{ITEM_NAME}/{REMAINING_ITEMS}",
        data={"structure_name": "Test Structure"})
    assert response.status_code == 200
    mock_append_json_file.assert_called_once_with(
        "generated as part of structure",
        [("structure name", "Test Structure")],
        f"{EXPECTED_JSON_DIR}/{ITEM_NAME}.json")
    mock_redirect.assert_called_once()
    mock_url_for.assert_called_once_with(
        "add.natural_gen_structure", item_name=ITEM_NAME, remaining_items=REMAINING_ITEMS)


@patch(f"{FILE_LOC}._append_json_file")
@patch(f"{FILE_LOC}.flash")
@patch(f"{FILE_LOC}.move_next_page")
def test_natural_gen_structure_with_next(
        mock_move_next_page, mock_flash, mock_append_json_file, client):
    response = client.post(
        f"/add_natural_gen_structure/{ITEM_NAME}/{REMAINING_ITEMS}",
        data={"structure_name": "Test Structure", "next": True})
    assert response.status_code == 200
    mock_append_json_file.assert_called_once_with(
        "generated as part of structure",
        [("structure name", "Test Structure")],
        f"{EXPECTED_JSON_DIR}/{ITEM_NAME}.json")
    mock_flash.assert_called_once()
    mock_move_next_page.assert_called_once_with(ITEM_NAME, REMAINING_ITEMS)


@pytest.mark.parametrize(
    ("villager_level", "has_villager_level", "other_item_required", "has_other"),
    [("Test Level", True, "Other Item", True),
     ("Test Level", True, "", False),
     ("", False, "Other Item", True),
     ("", False, "", False)])
@patch(f"{FILE_LOC}._append_json_file")
@patch(f"{FILE_LOC}.flash")
@patch(f"{FILE_LOC}.move_next_page")
def test_trading(
        mock_move_next_page, mock_flash, mock_append_json_file,
        villager_level, has_villager_level, other_item_required, has_other, client):
    form_data = {"villager_type": "Test Villager", "emerald_price": "1"}
    # expected_data = {
    #     "villager type": "Test Villager",
    #     "villager level": villager_level,
    #     "emerald price": 1,
    #     "other item required": other_item_required}
    if has_other:
        form_data["other_item"] = other_item_required
    if has_villager_level:
        form_data["villager_level"] = villager_level

    response = client.post(f"/add_trading/{ITEM_NAME}/{REMAINING_ITEMS}", data=form_data)
    assert response.status_code == 200
    mock_append_json_file.assert_called_once_with(
        "trading",
        [("villager type", "Test Villager"),
         ("villager level", villager_level, has_villager_level),
         ("emerald price", 1),
         ("other item required", other_item_required, has_other)],
        f"{EXPECTED_JSON_DIR}/{ITEM_NAME}.json")
    mock_flash.assert_called_once()
    mock_move_next_page.assert_called_once_with(ITEM_NAME, REMAINING_ITEMS)


@pytest.mark.parametrize(
    ("has_part", "part_of", "has_generated", "generated"),
    [(True, "Test Part Of", True, "Test Generated"),
     (True, "Test Part Of", False, ""),
     (False, "", True, "Test Generated"),
     (False, "", False, "")])
@patch(f"{FILE_LOC}._append_json_file")
@patch(f"{FILE_LOC}.flash")
@patch(f"{FILE_LOC}.move_next_page")
def test_post_gen(
        mock_move_next_page, mock_flash, mock_append_json_file, has_part, part_of,
        has_generated, generated, client):
    form_data = {}
    if has_part:
        form_data["part_of"] = part_of
    if has_generated:
        form_data["generated_from"] = generated
    # expected_data = {"part of": part_of, "generated from": generated}
    response = client.post(f"/add_post_generation/{ITEM_NAME}/{REMAINING_ITEMS}", data=form_data)
    assert response.status_code == 200
    mock_append_json_file.assert_called_once_with(
        "post generation",
        [("part of", part_of, has_part),
         ("generated from", generated, has_generated)],
        f"{EXPECTED_JSON_DIR}/{ITEM_NAME}.json")
    mock_flash.assert_called_once()
    mock_move_next_page.assert_called_once_with(ITEM_NAME, REMAINING_ITEMS)


@patch(f"{FILE_LOC}._append_json_file")
@patch(f"{FILE_LOC}.flash")
@patch(f"{FILE_LOC}.redirect")
@patch(f"{FILE_LOC}.url_for")
def test_stonecutter(mock_url_for, mock_redirect, mock_flash, mock_append_json_file, client):
    response = client.post(
        f"/add_stonecutter/{ITEM_NAME}/{REMAINING_ITEMS}",
        data={"other_block": "Test Item 2", "quantity": 1})
    mock_append_json_file.assert_called_once_with(
        "stonecutter", [("block required", "Test Item 2", "quantity", 1)],
        f"{EXPECTED_JSON_DIR}/{ITEM_NAME}.json")
    mock_flash.assert_called_once()
    mock_url_for.assert_called_once_with(
        "add.stonecutter", item_name=ITEM_NAME, remaining_items=REMAINING_ITEMS)
    mock_redirect.assert_called_once()


@patch(f"{FILE_LOC}._append_json_file")
@patch(f"{FILE_LOC}.flash")
@patch(f"{FILE_LOC}.move_next_page")
def test_stonecutter(mock_move_next_page, mock_flash, mock_append_json_file, client):
    response = client.post(
        f"/add_stonecutter/{ITEM_NAME}/{REMAINING_ITEMS}",
        data={"other_block": "Test Item 2", "quantity": 1, "next": ""})
    mock_append_json_file.assert_called_once()
    mock_flash.assert_called_once()
    mock_move_next_page.assert_called_once_with(ITEM_NAME, REMAINING_ITEMS)

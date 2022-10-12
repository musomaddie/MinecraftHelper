from unittest.mock import call, patch

import pytest

import block_adder_flask.manual_population as pop

ITEM_NAME = "Test Item"
GROUP_NAME = "Test Group"

FILE_LOC = "block_adder_flask.manual_population"
EXPECTED_JSON_DIR = "block_adder_flask/item_information"
DEFAULT_VALUES_FROM_GROUP = "[]"


@patch(f"{FILE_LOC}.open")
@patch(f"{FILE_LOC}.json.load", return_value={"items": []})
@patch(f"{FILE_LOC}.update_json_file")
def test_add_to_item_list(mock_update_json_file, mock_json_load, mock_open):
    pop._add_to_item_list(ITEM_NAME)
    mock_update_json_file.assert_called_once_with(
        {"items": [ITEM_NAME]}, f"{EXPECTED_JSON_DIR}/item_list.json")
    mock_open.assert_called_once_with(f"{EXPECTED_JSON_DIR}/item_list.json")
    mock_json_load.assert_called_once()


@patch(f"{FILE_LOC}.open")
@patch(f"{FILE_LOC}.json.load", return_value={"items": [ITEM_NAME]})
@patch(f"{FILE_LOC}.update_json_file")
def test_add_to_item_list_already_present(mock_update_json_file, mock_json_load, mock_open):
    pop._add_to_item_list(ITEM_NAME)
    mock_update_json_file.assert_called_once_with(
        {"items": [ITEM_NAME]}, f"{EXPECTED_JSON_DIR}/item_list.json")
    mock_open.assert_called_once_with(f"{EXPECTED_JSON_DIR}/item_list.json")
    mock_json_load.assert_called_once()


@patch(f"{FILE_LOC}.redirect")
@patch(f"{FILE_LOC}.url_for")
def test_continue_work(mock_url_for, mock_redirect):
    pop.continue_work(ITEM_NAME, True, "current")
    mock_url_for.assert_called_once_with("current", item_name=ITEM_NAME)
    mock_redirect.assert_called_once()


@patch(f"{FILE_LOC}.move_next_page")
def test_continue_work_next(mock_move_next_page):
    pop.continue_work(ITEM_NAME, False, "current")
    mock_move_next_page.assert_called_once_with(ITEM_NAME)


@patch(f"{FILE_LOC}.join")
@patch(f"{FILE_LOC}.isfile", return_value=True)
@patch(f"{FILE_LOC}.get_file_contents")
@patch(f"{FILE_LOC}._add_to_item_list")
@patch(f"{FILE_LOC}.get_group", return_value=GROUP_NAME)
@patch(f"{FILE_LOC}.ExistingGroupInfo")
@patch(f"{FILE_LOC}.save_to_group")
def test_add_item_get_file_exists(
        mock_save_to_group,
        mock_already_existing_group,
        mock_get_group,
        mock_add_to_item_list,
        mock_get_file_contents,
        mock_isfile,
        mock_join,
        client):
    mock_already_existing_group.should_show = True
    response = client.get(f"/add_item/{ITEM_NAME}")
    assert response.status_code == 200
    mock_save_to_group.assert_called_once_with(GROUP_NAME, ITEM_NAME)
    assert call.load_from_session(GROUP_NAME, ITEM_NAME) in mock_already_existing_group.mock_calls
    mock_join.assert_called_once_with("block_adder_flask/item_information", "Test Item.json")
    mock_isfile.assert_called_once()
    mock_get_file_contents.assert_called_once_with(f"{EXPECTED_JSON_DIR}/{ITEM_NAME}.json")
    mock_add_to_item_list.assert_called_once_with(ITEM_NAME)
    mock_get_group.assert_called_once_with(ITEM_NAME)


@patch(f"{FILE_LOC}.join")
@patch(f"{FILE_LOC}.isfile", return_value=False)
@patch(f"{FILE_LOC}.update_json_file")
@patch(f"{FILE_LOC}.get_group", return_value=GROUP_NAME)
@patch(f"{FILE_LOC}.ExistingGroupInfo")
@patch(f"{FILE_LOC}.save_to_group")
def test_add_item_get_doesnt_already_exist_with_mocks(
        mock_save_to_group, mock_already_existing_group, mock_get_group,
        mock_update_json_file, mock_isfile, mock_join, app, client):
    response = client.get(f"/add_item/{ITEM_NAME}")
    assert response.status_code == 200
    mock_save_to_group.assert_called_once_with(GROUP_NAME, ITEM_NAME)
    assert call.load_from_session(GROUP_NAME, ITEM_NAME) in mock_already_existing_group.mock_calls
    mock_join.assert_called_once_with("block_adder_flask/item_information", "Test Item.json")
    mock_isfile.assert_called_once()
    mock_update_json_file.assert_called_once_with(
        {"name": ITEM_NAME}, f"{EXPECTED_JSON_DIR}/{ITEM_NAME}.json")
    mock_get_group.assert_called_once_with(ITEM_NAME)


@patch(f"{FILE_LOC}.isfile")
@patch(f"{FILE_LOC}.get_group")
@patch(f"{FILE_LOC}.get_updated_group_name")
@patch(f"{FILE_LOC}.update_json_file")
@patch(f"{FILE_LOC}.url_for")
@patch(f"{FILE_LOC}.redirect")
@patch(f"{FILE_LOC}.ExistingGroupInfo")
@patch(f"{FILE_LOC}.save_to_group")
@patch(f"{FILE_LOC}.remove_from_group")
def test_add_item_update_group(
        mock_remove_from_group, mock_save_to_group, mock_already_existing_group, mock_redirect,
        mock_url_for, mock_update_file, mock_get_group_name, mock_get_group, mock_isfile, client):
    mock_isfile.return_value = False
    response = client.post(
        f"/add_item/{ITEM_NAME}",
        data={"update_group": True, "group_name_replacement": "New Group"})
    assert response.status_code == 200
    mock_remove_from_group.assert_called_once_with(mock_get_group_name.return_value, ITEM_NAME)
    mock_save_to_group.assert_has_calls(
        [call(mock_get_group_name.return_value, ITEM_NAME),
         call("New Group", ITEM_NAME)])
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


@patch(f"{FILE_LOC}.join")
@patch(f"{FILE_LOC}.isfile", return_value=False)
@patch(f"{FILE_LOC}.update_json_file")
@patch(f"{FILE_LOC}.get_updated_group_name")
@patch(f"{FILE_LOC}.get_group")
@patch(f"{FILE_LOC}.save_to_group")
@patch(f"{FILE_LOC}.ExistingGroupInfo")
@patch(f"{FILE_LOC}.url_for")
@patch(f"{FILE_LOC}.redirect")
def test_add_item_use_group_values(
        mock_redirect, mock_url_for, mock_existing_group_info, mock_save_to_group, mock_get_group,
        mock_get_updated_group_name, mock_update_json_file,
        mock_isfile, mock_join, client):
    response = client.post(
        f"/add_item/{ITEM_NAME}", data={"load_from_existing_group": ""}
    )
    assert response.status_code == 200
    assert call.load_from_session().use_values_button_clicked() in \
           mock_existing_group_info.mock_calls
    mock_url_for.assert_called_once_with("add.item", item_name=ITEM_NAME)


@patch(f"{FILE_LOC}.join")
@patch(f"{FILE_LOC}.isfile", return_value=False)
@patch(f"{FILE_LOC}.update_json_file")
@patch(f"{FILE_LOC}.get_group")
@patch(f"{FILE_LOC}.get_updated_group_name")
@patch(f"{FILE_LOC}.save_to_group")
@patch(f"{FILE_LOC}.ExistingGroupInfo")
@patch(f"{FILE_LOC}.move_next_page")
def test_add_item_all_methods_selected(
        mock_move_next_page, mock_already_entered_info, mock_save_to_group,
        mock_get_group_name, mock_get_group, mock_update_file, mock_isfile, mock_join, client):
    with patch(f"{FILE_LOC}.session", dict()) as session:
        response = client.post(
            f"/add_item/{ITEM_NAME}",
            data={"breaking": "", "breaking_other": "", "crafting": "", "fishing": "",
                  "trading": "",
                  "nat_gen": "", "nat_biome": "", "nat_struct": "", "post_gen": "",
                  "stonecutter": ""}
        )
        assert response.status_code == 200
        assert "remaining_methods" in session
        assert session["remaining_methods"] == [
            "add.breaking", "add.breaking_other", "add.crafting", "add.fishing", "add.trading",
            "add.natural_generation", "add.natural_generation_biome", "add.natural_gen_structure",
            "add.post_generation", "add.stonecutter"]

    mock_join.assert_called_once_with(EXPECTED_JSON_DIR, f"{ITEM_NAME}.json")
    mock_isfile.assert_called_once()
    mock_update_file.assert_called_once_with(
        {"name": ITEM_NAME}, f"{EXPECTED_JSON_DIR}/{ITEM_NAME}.json")
    mock_get_group.assert_called_once_with(ITEM_NAME)
    mock_get_group_name.assert_called_once_with(
        mock_get_group.return_value, {"name": ITEM_NAME})
    mock_save_to_group.assert_called_once_with(mock_get_group_name.return_value, ITEM_NAME)
    mock_already_entered_info.assert_has_calls(
        [call.load_from_session(mock_get_group_name.return_value, ITEM_NAME)]
    )
    mock_move_next_page.assert_called_once_with(ITEM_NAME)


@pytest.mark.parametrize(
    ("tool_form_value", "specific_tool", "silk_form_value", "fastest_tool", "move_another"),
    [("tool_no", "", "silk_no", "", True),
     ("tool_no", "", "silk_no", "", False),
     ("tool_yes", "", "silk_no", "", True),
     ("tool_yes", "", "silk_no", "", False),
     ("tool_specific", "pickaxe", "silk_no", "", True),
     ("tool_specific", "pickaxe", "silk_no", "", False),
     ("tool_no", "", "silk_no", "axe", True),
     ("tool_no", "", "silk_no", "axe", False),
     ("tool_yes", "", "silk_no", "axe", True),
     ("tool_yes", "", "silk_no", "axe", False),
     ("tool_specific", "pickaxe", "silk_no", "axe", True),
     ("tool_specific", "pickaxe", "silk_no", "axe", False),
     ("tool_no", "", "silk_yes", "", True),
     ("tool_no", "", "silk_yes", "", False),
     ("tool_yes", "", "silk_yes", "", True),
     ("tool_yes", "", "silk_yes", "", False),
     ("tool_specific", "pickaxe", "silk_yes", "", True),
     ("tool_specific", "pickaxe", "silk_yes", "", False),
     ("tool_no", "", "silk_yes", "axe", True),
     ("tool_no", "", "silk_yes", "axe", False),
     ("tool_yes", "", "silk_yes", "axe", True),
     ("tool_yes", "", "silk_yes", "axe", False),
     ("tool_specific", "pickaxe", "silk_yes", "axe", True),
     ("tool_specific", "pickaxe", "silk_yes", "axe", False)])
@patch(f"{FILE_LOC}.append_json_file")
@patch(f"{FILE_LOC}.flash")
@patch(f"{FILE_LOC}.continue_work")
def test_breaking(
        mock_continue_work, mock_flash, mock_append_json_file,
        tool_form_value, specific_tool, silk_form_value, fastest_tool, move_another, client):
    form_data = {"requires_tool": tool_form_value,
                 "specific_tool": specific_tool,
                 "requires_silk": silk_form_value,
                 "fastest_specific_tool": fastest_tool}
    if move_another:
        form_data["another"] = ""
    if fastest_tool != "":
        form_data["fastest_tool"] = ""
    response = client.post(f"/add_breaking/{ITEM_NAME}", data=form_data)
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
    mock_continue_work.assert_called_once_with(ITEM_NAME, move_another, "add.breaking")


@patch(f"{FILE_LOC}.append_json_file")
@patch(f"{FILE_LOC}.flash")
@patch(f"{FILE_LOC}.continue_work")
def test_breaking_other(mock_continue_work, mock_flash, mock_append_json_file, client):
    response = client.post(
        f"/add_breaking_other/{ITEM_NAME}",
        data={"other_block": "Other Block", "percent_dropping": 10.12, "fortune": ""})
    assert response.status_code == 200
    mock_append_json_file.assert_called_once_with(
        "breaking other", [
            ("other block name", "Other Block"),
            ("likelihood of dropping", 10.12, True),
            ("helped with fortune", True)],
        f"{EXPECTED_JSON_DIR}/{ITEM_NAME}.json")
    mock_flash.assert_called_once()
    mock_continue_work.assert_called_once_with(ITEM_NAME, False, "add.breaking_other")


@pytest.mark.parametrize("should_add_another", [True, False])
@patch(f"{FILE_LOC}.append_json_file")
@patch(f"{FILE_LOC}.flash")
@patch(f"{FILE_LOC}.continue_work")
def test_crafting(
        mock_continue_work, mock_flash, mock_append_json_file, should_add_another, client):
    form_data = {
        "cs1": "Item 1", "cs2": "Item 2", "cs3": "Item 3", "cs4": "Item 4", "cs5": "Item 5",
        "cs6": "Item 6", "cs7": "Item 7", "cs8": "Item 8", "cs9": "Item 9",
        "n_created": 1, "works_four": "", "exact_positioning": ""
    }
    if should_add_another:
        form_data["another"] = ""
    expected_data = [
        ("crafting slots",
         ["Item 1", "Item 2", "Item 3", "Item 4", "Item 5", "Item 6", "Item 7", "Item 8",
          "Item 9"]),
        ("num created", 1),
        ("works with four by four", True),
        ("requires exact positioning", True)]
    response = client.post(f"/add_crafting/{ITEM_NAME}", data=form_data)
    assert response.status_code == 200
    mock_append_json_file.assert_called_once_with(
        "crafting", expected_data, f"{EXPECTED_JSON_DIR}/{ITEM_NAME}.json")
    mock_flash.assert_called_once()
    mock_continue_work.assert_called_once_with(ITEM_NAME, should_add_another, "add.crafting")


@patch(f"{FILE_LOC}.append_json_file")
@patch(f"{FILE_LOC}.flash")
@patch(f"{FILE_LOC}.continue_work")
def test_fishing(mock_continue_work, mock_flash, mock_append_json_file, client):
    response = client.post(
        f"/add_fishing/{ITEM_NAME}", data={"item_level": "Treasure"})
    assert response.status_code == 200
    mock_append_json_file.assert_called_once_with(
        "fishing", [("treasure type", "Treasure")], f"{EXPECTED_JSON_DIR}/{ITEM_NAME}.json")
    mock_flash.assert_called_once()
    mock_continue_work.assert_called_once_with(ITEM_NAME, False, "add.fishing")


@pytest.mark.parametrize(
    ("has_container", "expected_container", "has_chance", "expected_chance", "should_add_another"),
    [(True, "Container 1", True, 50, True),
     (True, "Container 1", True, 50, False),
     (True, "Container 1", False, 100, True),
     (True, "Container 1", False, 100, False,),
     (False, "", True, 50, True),
     (False, "", True, 50, False),
     (False, "", False, 100, True),
     (False, "", False, 100, False)]
)
@patch(f"{FILE_LOC}.append_json_file")
@patch(f"{FILE_LOC}.flash")
@patch(f"{FILE_LOC}.continue_work")
def test_natural_generation(
        mock_continue_work, mock_flash, mock_append_json_file,
        has_container, expected_container, has_chance, expected_chance, should_add_another, client):
    form_data = {"structure": "Structure 1", "quantity_fd": 1}
    if has_container:
        form_data["container"] = expected_container
    if has_chance:
        form_data["chance"] = expected_chance
    if should_add_another:
        form_data["another"] = ""

    response = client.post(f"/add_natural_generation/{ITEM_NAME}", data=form_data)
    assert response.status_code == 200
    mock_append_json_file.assert_called_once_with(
        "generated in chests",
        [("structure", "Structure 1"),
         ("container", expected_container, has_container),
         ("quantity", 1),
         ("chance", expected_chance, has_chance)],
        f"{EXPECTED_JSON_DIR}/{ITEM_NAME}.json")
    mock_flash.assert_called_once()
    mock_continue_work.assert_called_once_with(
        ITEM_NAME, should_add_another, "add.natural_generation")


@pytest.mark.parametrize("should_add_another", [True, False])
@patch(f"{FILE_LOC}.append_json_file")
@patch(f"{FILE_LOC}.flash")
@patch(f"{FILE_LOC}.continue_work")
def test_natural_generation_biome(
        mock_continue_work, mock_flash, mock_append_json_file, should_add_another, client):
    form_data = {"biome": "Test Biome"}
    if should_add_another:
        form_data["another"] = ""
    response = client.post(f"/add_natural_biome/{ITEM_NAME}", data=form_data)
    assert response.status_code == 200
    mock_append_json_file.assert_called_once_with(
        "generated in biome", [("biome name", "Test Biome")],
        f"{EXPECTED_JSON_DIR}/{ITEM_NAME}.json")
    mock_flash.assert_called_once()
    mock_continue_work.assert_called_once_with(
        ITEM_NAME, should_add_another, "add.natural_generation_biome")


@pytest.mark.parametrize("should_add_another", [True, False])
@patch(f"{FILE_LOC}.append_json_file")
@patch(f"{FILE_LOC}.flash")
@patch(f"{FILE_LOC}.continue_work")
def test_natural_gen_structure(
        mock_continue_work, mock_flash, mock_append_json_file, should_add_another, client):
    form_data = {"structure_name": "Test Structure"}
    if should_add_another:
        form_data["another"] = ""
    response = client.post(f"/add_natural_gen_structure/{ITEM_NAME}", data=form_data)
    assert response.status_code == 200
    mock_append_json_file.assert_called_once_with(
        "generated as part of structure",
        [("structure name", "Test Structure")],
        f"{EXPECTED_JSON_DIR}/{ITEM_NAME}.json")
    mock_flash.assert_called_once()
    mock_continue_work.assert_called_once_with(
        ITEM_NAME, should_add_another, "add.natural_gen_structure")


@pytest.mark.parametrize(
    ("villager_level", "has_villager_level", "other_item_required", "has_other"),
    [("Test Level", True, "Other Item", True),
     ("Test Level", True, "", False),
     ("", False, "Other Item", True),
     ("", False, "", False)])
@patch(f"{FILE_LOC}.append_json_file")
@patch(f"{FILE_LOC}.flash")
@patch(f"{FILE_LOC}.continue_work")
def test_trading(
        mock_continue_work, mock_flash, mock_append_json_file,
        villager_level, has_villager_level, other_item_required, has_other, client):
    form_data = {"villager_type": "Test Villager", "emerald_price": "1"}
    if has_other:
        form_data["other_item"] = other_item_required
    if has_villager_level:
        form_data["villager_level"] = villager_level

    response = client.post(f"/add_trading/{ITEM_NAME}", data=form_data)
    assert response.status_code == 200
    mock_append_json_file.assert_called_once_with(
        "trading",
        [("villager type", "Test Villager"),
         ("villager level", villager_level, has_villager_level),
         ("emerald price", 1),
         ("other item required", other_item_required, has_other)],
        f"{EXPECTED_JSON_DIR}/{ITEM_NAME}.json")
    mock_flash.assert_called_once()
    mock_continue_work.assert_called_once_with(ITEM_NAME, False, "add.trading")


@pytest.mark.parametrize(
    ("has_part", "part_of", "has_generated", "generated"),
    [(True, "Test Part Of", True, "Test Generated"),
     (True, "Test Part Of", False, ""),
     (False, "", True, "Test Generated"),
     (False, "", False, "")])
@patch(f"{FILE_LOC}.append_json_file")
@patch(f"{FILE_LOC}.flash")
@patch(f"{FILE_LOC}.continue_work")
def test_post_gen(
        mock_continue_work, mock_flash, mock_append_json_file, has_part, part_of,
        has_generated, generated, client):
    form_data = {}
    if has_part:
        form_data["part_of"] = part_of
    if has_generated:
        form_data["generated_from"] = generated
    response = client.post(f"/add_post_generation/{ITEM_NAME}", data=form_data)
    assert response.status_code == 200
    mock_append_json_file.assert_called_once_with(
        "post generation",
        [("part of", part_of, has_part),
         ("generated from", generated, has_generated)],
        f"{EXPECTED_JSON_DIR}/{ITEM_NAME}.json")
    mock_flash.assert_called_once()
    mock_continue_work.assert_called_once_with(ITEM_NAME, False, "add.post_generation")


@pytest.mark.parametrize("should_add_another", [True, False])
@patch(f"{FILE_LOC}.append_json_file")
@patch(f"{FILE_LOC}.flash")
@patch(f"{FILE_LOC}.continue_work")
def test_stonecutter(
        mock_continue_work, mock_flash, mock_append_json_file, should_add_another, client):
    form_data = {"other_block": "Test Item 2", "quantity": 1}
    if should_add_another:
        form_data["another"] = ""
    response = client.post(f"/add_stonecutter/{ITEM_NAME}", data=form_data)
    mock_append_json_file.assert_called_once_with(
        "stonecutter", [("block required", "Test Item 2"), ("quantity made", 1)],
        f"{EXPECTED_JSON_DIR}/{ITEM_NAME}.json")
    mock_flash.assert_called_once()
    mock_continue_work.assert_called_once_with(ITEM_NAME, should_add_another, "add.stonecutter")

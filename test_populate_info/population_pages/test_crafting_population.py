import pytest

import populate_info.resources as r
from conftest import ITEM_1, ITEM_2, ITEM_3, assert_dictionary_values, get_file_contents
from populate_info.population_pages.crafting_population import crafting_json_to_html_ids


class TestCraftingJsonToHtml:
    @pytest.fixture
    def crafting_json(self):
        return {"slots": {"1": ITEM_1}, "number created": 1,
                "works in smaller grid": False, "relative positioning": "strict"}

    @pytest.mark.parametrize(
        ("json_slots", "html_slots"),
        [({"1": ITEM_1}, {"cs1": ITEM_1}),
         ({"2": ITEM_1}, {"cs2": ITEM_1}),
         ({"3": ITEM_1}, {"cs3": ITEM_1}),
         ({"4": ITEM_1}, {"cs4": ITEM_1}),
         ({"5": ITEM_1}, {"cs5": ITEM_1}),
         ({"6": ITEM_1}, {"cs6": ITEM_1}),
         ({"7": ITEM_1}, {"cs7": ITEM_1}),
         ({"8": ITEM_1}, {"cs8": ITEM_1}),
         ({"9": ITEM_1}, {"cs9": ITEM_1}),
         ({"1": ITEM_1, "5": ITEM_2, "9": ITEM_3}, {"cs1": ITEM_1, "cs5": ITEM_2, "cs9": ITEM_3})]
    )
    def test_slots(self, json_slots, html_slots, crafting_json):
        crafting_json["slots"] = json_slots
        result = crafting_json_to_html_ids(crafting_json)
        assert_dictionary_values(
            result["to_fill"],
            [(key, value) for key, value in html_slots.items()],
            assert_exact=False)

    def test_number(self, crafting_json):
        crafting_json["number created"] = 2
        result = crafting_json_to_html_ids(crafting_json)
        assert_dictionary_values(
            result["to_fill"],
            [("number_created", 2)],
            assert_exact=False
        )

    def test_checked_still_exists_no_data(self, crafting_json):
        assert "to_mark_checked" in crafting_json_to_html_ids(crafting_json)

    @pytest.mark.parametrize(
        ("json_smaller_grid", "is_expected_in_html"),
        [(True, True),
         (False, False)]
    )
    def test_smaller_grid_true(self, json_smaller_grid, is_expected_in_html, crafting_json):
        crafting_json["works in smaller grid"] = json_smaller_grid
        result = crafting_json_to_html_ids(crafting_json)
        assert is_expected_in_html == ("works_in_four_cbox" in result["to_mark_checked"])

    @pytest.mark.parametrize(
        ("json_relative_positioning", "is_expected_in_html"),
        [("strict", False), ("flexible", True)])
    def test_relative_positioning(self, json_relative_positioning, is_expected_in_html, crafting_json):
        crafting_json["relative positioning"] = json_relative_positioning
        result = crafting_json_to_html_ids(crafting_json)
        assert is_expected_in_html == ("flexible_positioning_cbox" in result["to_mark_checked"])


class TestPost:
    def test_crafting_post(self, client, session_with_group, item_file_name_only):
        response = client.post(
            f"/crafting/{ITEM_1}", data={
                "cs1": ITEM_2,
                "cs2": "",
                "cs3": ITEM_3,
                "cs4": "",
                "cs5": "",
                "cs6": "",
                "cs7": "",
                "cs8": "",
                "cs9": "",
                "number_created": 2
            }
        )
        assert response.status_code == 302
        assert_dictionary_values(
            get_file_contents(r.get_item_fn(ITEM_1))[r.CRAFTING_CAT_KEY],
            [(r.CRAFTING_SLOTS_J_KEY, {"1": ITEM_2, "3": ITEM_3}),
             (r.CRAFTING_N_CREATED_J_KEY, "2"),
             (r.CRAFTING_SMALL_GRID_J_KEY, False),
             (r.CRAFTING_RELATIVE_POSITIONING_J_KEY, "strict")])


def test_crafting_get(client, session_with_group):
    response = client.get("/crafting/Testing Item")
    assert response.status_code == 200

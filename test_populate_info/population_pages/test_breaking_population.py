import pytest

import populate_info.resources as r
from conftest import ITEM_1, assert_dictionary_values, get_file_contents
from populate_info.population_pages.breaking_population import breaking_json_to_html_ids

r_tool = "Iron Axe"
r_tool_expected = "iron-axe"
f_tool = "Shears"
f_tool_expected = "shears"

item_1_json = {"requires tool": "none", "silk touch": False}
item_1_html = {
    "to-mark-checked": ["requires-tool-no", "requires-silk-no", "fastest-tool-no"],
    "button-choice": "another"
}

item_2_json = {"requires tool": "any", "silk touch": False}
item_2_html = {
    "to-mark-checked": ["requires-tool-any", "requires-silk-no", "fastest-tool-no"],
    "button-choice": "another"
}

item_3_json = {"requires tool": "none", "silk touch": True}
item_3_html = {
    "to-mark-checked": ["requires-tool-no", "requires-silk-yes", "fastest-tool-no"],
    "button-choice": "next"
}


class TestBreakingJsonToHtmlIds:

    @pytest.fixture
    def default_group_data(self):
        return {
            "requires tool": "any",
            "silk touch": False,
        }

    @pytest.mark.parametrize(
        ("input_tool_value", "expected_value"),
        [("any", "requires-tool-any"),
         ("none", "requires-tool-no"),
         ("specific", "requires-tool-spec")]
    )
    def test_requires_tool(self, input_tool_value, expected_value, default_group_data):
        default_group_data["requires tool"] = input_tool_value
        if input_tool_value == "specific":
            default_group_data["required tool"] = r_tool

        result = breaking_json_to_html_ids(default_group_data, {})

        assert expected_value in result["to-mark-checked"]

    @pytest.mark.parametrize(
        ("input_silk_touch", "expected_value"),
        [(True, "requires-silk-yes"), (False, "requires-silk-no")]
    )
    def test_silk_touch(self, input_silk_touch, expected_value, default_group_data):
        default_group_data["silk touch"] = input_silk_touch

        result = breaking_json_to_html_ids(default_group_data, {})

        assert expected_value in result["to-mark-checked"]

    def test_required_tool(self, default_group_data):
        default_group_data["requires tool"] = "specific"
        default_group_data["required tool"] = r_tool

        result = breaking_json_to_html_ids(default_group_data, {})

        assert r_tool_expected == result["dropdown-select"]["specific-tool-select"]

    def test_fastest_tool(self, default_group_data):
        default_group_data["fastest tool"] = f_tool

        result = breaking_json_to_html_ids(default_group_data, {})

        assert "fastest-tool-yes" in result["to-mark-checked"]
        assert f_tool.lower() == result["dropdown-select"]["fastest-specific-tool-select"]

    @pytest.mark.parametrize(
        ("item_data", "expected_result"),
        [
            # 0 / 3
            ({}, item_1_html),
            # 1 / 3
            (item_1_json, item_2_html),
            # 2/ 3
            ([item_1_json, item_2_json], item_3_html)])
    def test_multiple_breaking_info(self, item_data, expected_result):
        # They use the same group data every time.
        group_data = [item_1_json, item_2_json, item_3_json]

        result = breaking_json_to_html_ids(group_data, item_data)

        assert_dictionary_values(
            result,
            [(key, value) for key, value in expected_result.items()],
            False)


class TestBreakingPost:

    def test_happy(self, client, session_with_group, item_file_name_only):
        response = client.post(
            f"/breaking/{ITEM_1}", data={
                "requires-tool": "tool-no",
                "requires-silk": "silk-no-v",
                "fastest-tool": "fastest-no",

            }
        )
        assert response.status_code == 302
        assert_dictionary_values(
            get_file_contents(r.get_item_fn(ITEM_1))[r.BREAKING_CAT_KEY],
            [("requires tool", "none"), ("silk touch", False)], True)

    # TODO - why haven't I actually tested this input fully?? (I should check there's nothing pending on windows).


def test_breaking_get(client, session_with_group, item_file_name_only):
    response = client.get(f"/breaking/{ITEM_1}")
    assert response.status_code == 200

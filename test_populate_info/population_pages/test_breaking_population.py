import pytest

import populate_info.resources as r
from conftest import ITEM_1, assert_dictionary_values, get_file_contents
from populate_info.population_pages.breaking_population import breaking_json_to_html_ids

r_tool = "Iron Axe"
r_tool_expected = "iron-axe"
f_tool = "Shears"
f_tool_expected = "shears"


class TestBreakingJsonToHtmlIds:

    @pytest.mark.parametrize(
        ("input_tool_value", "expected_value"),
        [("any", "requires-tool-any"),
         ("none", "requires-tool-no"),
         ("specific", "requires-tool-spec")]
    )
    def test_requires_tool(self, input_tool_value, expected_value):
        if input_tool_value == "specific":
            result = breaking_json_to_html_ids(
                {"requires tool": input_tool_value, "required tool": r_tool, "silk touch": False}
            )
        else:
            result = breaking_json_to_html_ids(
                {"requires tool": input_tool_value, "silk touch": False}
            )
        assert expected_value in result["to-mark-checked"]

    @pytest.mark.parametrize(
        ("input_silk_touch", "expected_value"),
        [(True, "requires-silk-yes"), (False, "requires-silk-no")]
    )
    def test_silk_touch(self, input_silk_touch, expected_value):
        result = breaking_json_to_html_ids(
            {"requires tool": "any", "silk touch": input_silk_touch})
        assert expected_value in result["to-mark-checked"]

    def test_required_tool(self):
        result = breaking_json_to_html_ids(
            {"requires tool": "specific", "required tool": r_tool, "silk touch": False}
        )
        assert r_tool_expected == result["dropdown-select"]["specific-tool-select"]

    def test_fastest_tool(self):
        result = breaking_json_to_html_ids(
            {"requires tool": "any", "silk touch": False, "fastest tool": f_tool}
        )
        assert "fastest-tool-yes" in result["to-mark-checked"]
        assert f_tool.lower() == result["dropdown-select"]["fastest-specific-tool-select"]


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
            get_file_contents(r.get_item_fn(ITEM_1)),
            [(r.BREAKING_CAT_KEY, {r.BREAKING_REQ_TOOL_KEY: "none", r.BREAKING_SILK_TOUCH_KEY: False})],
            assert_exact=False)

    # TODO - why haven't I actually tested this input fully?? (I should check there's nothing pending on windows).


def test_breaking_get(client, session_with_group):
    response = client.get("/breaking/Testing Item")
    assert response.status_code == 200

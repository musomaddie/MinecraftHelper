import pytest

import populate_info.resources as r
from populate_info.population_pages.breaking_population import breaking_json_to_html_ids

r_tool = "Iron Axe"
r_tool_expected = "iron_axe"
f_tool = "Shears"
f_tool_expected = "shears"


@pytest.mark.parametrize(
    ("input_tool_value", "expected_value"),
    [("any", "requires_tool_any"),
     ("none", "requires_tool_no"),
     ("specific", "requires_tool_spec")]
)
def test_breaking_json_to_html_ids_requires_tool(input_tool_value, expected_value):
    if input_tool_value == "specific":
        result = breaking_json_to_html_ids(
            {"requires tool": input_tool_value, "required tool": r_tool, "silk touch": False}
        )
    else:
        result = breaking_json_to_html_ids(
            {"requires tool": input_tool_value, "silk touch": False}
        )
    assert expected_value in result["to_mark_checked"]


@pytest.mark.parametrize(
    ("input_silk_touch", "expected_value"),
    [(True, "requires_silk_yes"), (False, "requires_silk_no")]
)
def test_breaking_json_to_html_ids_silk_touch(input_silk_touch, expected_value):
    result = breaking_json_to_html_ids(
        {"requires tool": "any", "silk touch": input_silk_touch})
    assert expected_value in result["to_mark_checked"]


def test_breaking_json_to_html_required_tool():
    result = breaking_json_to_html_ids(
        {"requires tool": "specific", "required tool": r_tool, "silk touch": False}
    )
    assert r_tool_expected in result["dropdown_select"]


def test_breaking_json_to_html_fastest_tool():
    result = breaking_json_to_html_ids(
        {"requires tool": "any", "silk touch": False, "fastest tool": f_tool}
    )
    assert "fastest_tool" in result["to_mark_checked"]
    assert f_tool_expected in result["dropdown_select"]


def test_breaking_get(client):
    with client.session_transaction() as session_before:
        session_before[r.GROUP_NAME_SK] = "group name"
    response = client.get("/breaking/Testsing Item")
    assert response.status_code == 200

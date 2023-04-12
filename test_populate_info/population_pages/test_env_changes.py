import pytest

from conftest import assert_dictionary_values
from populate_info.population_pages.env_changes_population import env_changes_json_to_html_ids


class TestEnvChangesJsonToHtml:
    @pytest.fixture
    def env_changes_json(self):
        return {"change": "change 1 description"}

    @pytest.fixture
    def env_changes_json_2(self):
        return [{"change": "change 1"}, {"change": "change 2"}]

    # TODO: for all of them, add a test for no items.

    def test_one_item_none_added(self, env_changes_json):
        result = env_changes_json_to_html_ids(env_changes_json, [])
        assert_dictionary_values(
            result,
            [("change_text", "change 1 description"),
             ("button_choice", "next")])

    def test_two_items_none_added(self, env_changes_json_2):
        result = env_changes_json_to_html_ids(env_changes_json_2, [])
        assert_dictionary_values(
            result,
            [("change_text", "change 1"), ("button_choice", "again")]
        )

    def test_two_items_one_added(self, env_changes_json_2):
        result = env_changes_json_to_html_ids(
            env_changes_json_2, {"change": "change 1"})
        assert_dictionary_values(
            result,
            [("change_text", "change 2"), ("button_choice", "next")]
        )

    def test_three_items_two_added(self, env_changes_json_2):
        env_changes_json_2.append({"change": "change 3"})
        result = env_changes_json_to_html_ids(
            env_changes_json_2, [{"change": "change 1"}, {"change": "change 2"}]
        )
        assert_dictionary_values(
            result,
            [("change_text", "change 3"), ("button_choice", "next")]
        )


def test_env_changes_get(client, session_with_group):
    response = client.get("/env_changes/Testing Item")
    assert response.status_code == 200

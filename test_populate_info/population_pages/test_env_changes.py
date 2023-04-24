import pytest

from conftest import assert_dictionary_values, ITEM_1
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
            [("change-text", "change 1 description"),
             ("button-choice", "next")])

    def test_two_items_none_added(self, env_changes_json_2):
        result = env_changes_json_to_html_ids(env_changes_json_2, [])
        assert_dictionary_values(
            result,
            [("change-text", "change 1"), ("button-choice", "another")]
        )

    def test_two_items_one_added(self, env_changes_json_2):
        result = env_changes_json_to_html_ids(
            env_changes_json_2, {"change": "change 1"})
        assert_dictionary_values(
            result,
            [("change-text", "change 2"), ("button-choice", "next")]
        )

    def test_three_items_two_added(self, env_changes_json_2):
        env_changes_json_2.append({"change": "change 3"})
        result = env_changes_json_to_html_ids(
            env_changes_json_2, [{"change": "change 1"}, {"change": "change 2"}]
        )
        assert_dictionary_values(
            result,
            [("change-text", "change 3"), ("button-choice", "next")]
        )


def test_env_changes_get(client, session_with_group, item_file_name_only):
    response = client.get(f"/env_changes/{ITEM_1}")
    assert response.status_code == 200

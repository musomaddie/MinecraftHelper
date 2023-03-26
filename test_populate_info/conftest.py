import json
from pathlib import Path

import pytest

import populate_info.resources as r
from populate_info import create_app

GROUP_1 = "Test Group 1"
GROUP_2 = "Test Group 2"
GROUP_3 = "Test Group 3"
ITEM_1 = "Test Item 1"
ITEM_2 = "Test Item 2"
ITEM_3 = "Test Item 3"


def _add_manual_test_group():
    with open(r.get_group_fn("testing_group"), "w") as f:
        json.dump(
            {"group name": "Testing",
             "items": ["Testing item", "Another item"],
             "breaking": {"some": "data"}},
            f)


def _create_file(filename, data):
    with open(filename, "w") as f:
        json.dump(data, f)


def get_file_contents(filename: str) -> dict:
    with open(filename) as f:
        return json.load(f)


def assert_dictionary_values(result, expected_key_value_pairs, assert_exact=True):
    if assert_exact:
        assert len(result) == len(expected_key_value_pairs), f"There are values in {result} that shouldn't be there"
    for expected_key, expected_value in zip(
            [l[0] for l in expected_key_value_pairs],
            [l[1] for l in expected_key_value_pairs]
    ):
        # TODO: look into pycharm not using my custom message.
        assert expected_key in result, f"{expected_key} is not found in {result}"
        assert result[expected_key] == expected_value, f"expected result[{expected_key}] to be {expected_value} but " \
                                                       f"was {result[expected_key]}"


@pytest.fixture
def app():
    app = create_app({"TESTING": True})
    return app


@pytest.fixture
def client(app):
    return app.test_client()


@pytest.fixture
def session_with_group(client):
    with client.session_transaction() as first_session:
        first_session[r.GROUP_NAME_SK] = GROUP_1
        first_session[r.METHOD_LIST_SK] = []


@pytest.fixture
def group_file_no_items():
    _create_file(r.get_group_fn(GROUP_1), {r.GROUP_NAME_KEY: GROUP_1, r.GROUP_ITEMS_KEY: []})
    return GROUP_1


@pytest.fixture
def group_file_with_1_item(tmp_path):
    """ Creates a group file with only one existing item (ITEM_1). Returns group_name."""
    _create_file(r.get_group_fn(GROUP_1),
                 {r.GROUP_NAME_KEY: GROUP_1, r.GROUP_ITEMS_KEY: [ITEM_1]})
    return GROUP_1


@pytest.fixture
def group_file_with_2_items():
    """ Creates a group file with some items. Returns group name."""
    _create_file(r.get_group_fn(GROUP_1),
                 {r.GROUP_NAME_KEY: GROUP_1, r.GROUP_ITEMS_KEY: [ITEM_1, ITEM_2]})
    return GROUP_1


@pytest.fixture
def group_file_all_categories():
    _create_file(r.get_group_fn(GROUP_1),
                 {r.GROUP_NAME_KEY: GROUP_1,
                  r.GROUP_ITEMS_KEY: [ITEM_1, ITEM_2],
                  r.BREAKING_CAT_KEY: {
                      "required tool": "any", "fastest tool": "Axe", "silk touch": False}})
    return GROUP_1


@pytest.fixture
def item_file_name_only():
    _create_file(r.get_item_fn(ITEM_1), {r.ITEM_NAME_KEY: ITEM_1})
    return ITEM_1


@pytest.fixture(autouse=True)
def create_tmp_dir(monkeypatch, tmp_path):
    Path(tmp_path / r.DIR).mkdir(parents=True)
    Path(tmp_path / r.DIR / "all_items").mkdir(parents=True)
    Path(tmp_path / r.DIR / "groups").mkdir(parents=True)
    # Monkeypatch these paths before creating any files.
    monkeypatch.chdir(tmp_path)
    _create_file(r.ADDED_ITEM_FN, {r.ITEM_LIST_KEY: []})
    _create_file(r.FULL_ITEMS_LIST_FN, {r.ITEM_LIST_KEY: [ITEM_1, ITEM_2, ITEM_3]})
    # While I have the tmp file hard-coded in prod I need to create it in the tests too.
    # TODO: delete this
    _add_manual_test_group()

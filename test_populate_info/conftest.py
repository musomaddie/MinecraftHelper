import json
from pathlib import Path

import pytest

import populate_info.population_pages.crafting_population
import populate_info.resources
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


def get_file_contents(filename: str) -> dict:
    """ Gets the content of the given file. """
    with open(filename) as f:
        return json.load(f)


def _create_file(filename, data):
    with open(filename, "w") as f:
        json.dump(data, f)


def assert_dictionary_values(result, expected_key_value_pairs, assert_exact=True):
    """ Checks if the given expected_key_value_pairs are in the dictionary passed as result. If assert_exact is True,
    the result should contain ONLY these values.

    I have to assign the value to be asserted to a variable prior to calling assert otherwise pytest won't use my
    custom assertion error messages. Not sure why :(
    """
    if assert_exact:
        expected_length = len(result) == len(expected_key_value_pairs)
        msg = f"{result} has more values then {expected_key_value_pairs}."
        assert expected_length, msg
    for expected_key, expected_value in zip(
            [l[0] for l in expected_key_value_pairs],
            [l[1] for l in expected_key_value_pairs]
    ):
        in_result = expected_key in result
        msg = f"KEY: {expected_key} ({type(expected_key)} not found in {result}"
        assert in_result, msg
        # Custom checking.
        if type(expected_value) == list:
            match_result = sorted(result[expected_key]) == sorted(expected_value)
        else:
            match_result = result[expected_key] == expected_value
        msg = f"expected result[{expected_key}] to be {expected_value} but was {result[expected_key]}"
        assert match_result, msg


@pytest.fixture
def app():
    app = create_app({"TESTING": True})
    return app


@pytest.fixture
def client(app):
    return app.test_client()


@pytest.fixture
def request_context(app):
    with app.test_request_context():
        yield


@pytest.fixture
def session_with_group(group_file_all_categories, client):
    with client.session_transaction() as first_session:
        first_session[r.SK_GROUP_NAME] = GROUP_1
        first_session[r.SK_METHOD_LIST] = []


@pytest.fixture
def group_file_no_items():
    _create_file(r.get_group_fn(GROUP_1), {r.KEY_GROUP_NAME: GROUP_1, r.KEY_GROUP_ITEMS: []})
    return GROUP_1


@pytest.fixture
def group_file_with_1_item(tmp_path):
    """ Creates a group file with only one existing item (ITEM_1). Returns name."""
    _create_file(r.get_group_fn(GROUP_1),
                 {r.KEY_GROUP_NAME: GROUP_1, r.KEY_GROUP_ITEMS: [ITEM_1]})
    return GROUP_1


@pytest.fixture
def group_file_with_2_items():
    """ Creates a group file with some items. Returns group name."""
    _create_file(r.get_group_fn(GROUP_1),
                 {r.KEY_GROUP_NAME: GROUP_1, r.KEY_GROUP_ITEMS: [ITEM_1, ITEM_2]})
    return GROUP_1


@pytest.fixture
def group_file_all_categories():
    _create_file(r.get_group_fn(GROUP_1),
                 {r.KEY_GROUP_NAME: GROUP_1,
                  r.KEY_GROUP_ITEMS: [ITEM_1, ITEM_2],
                  populate_info.resources.CK_BREAKING: {
                      "requires tool": "any", "fastest tool": "Axe", "silk touch": False},
                  r.CK_CRAFTING: {
                      "slots": {"1": ITEM_1, "2": ITEM_2, "3": ITEM_3},
                      "number created": 1,
                      "relative positioning": "strict",
                      "works in smaller grid": False},
                  r.CK_ENV_CHANGES: {"change": "description 1"}
                  })
    return GROUP_1


@pytest.fixture
def item_file_name_only():
    _create_file(r.get_item_fn(ITEM_1), {r.KEY_ITEM_NAME: ITEM_1})
    return ITEM_1


@pytest.fixture(autouse=True)
def create_tmp_dir(monkeypatch, tmp_path):
    # TODO revisit this once clean up is complete.
    Path(tmp_path / r.DIR).mkdir(parents=True)
    Path(tmp_path / r.DIR / "all_items").mkdir(parents=True)
    Path(tmp_path / r.DIR / "groups").mkdir(parents=True)
    # Monkeypatch these paths before creating any files.
    monkeypatch.chdir(tmp_path)
    _create_file(r.ADDED_ITEM_FN, {r.KEY_ITEM_LIST: []})
    _create_file(r.FULL_ITEMS_LIST_FN, {r.KEY_ITEM_LIST: [ITEM_1, ITEM_2, ITEM_3]})
    # While I have the tmp file hard-coded in prod I need to create it in the tests too.
    # TODO: delete this
    _add_manual_test_group()

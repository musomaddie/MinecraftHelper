import json
import os

import pytest

import populate_info.resources as r
from populate_info import create_app

NEW_GROUP = "New Group"
EXISTING_GROUP = "Test Group"
TEST_ITEM = "Test Item"


def _wipe_added_blocks():
    with open(r.ADDED_ITEM_FN, "w") as f:
        json.dump({r.ITEM_LIST_KEY: []}, f)


def _wipe_existing_group():
    with open(r.get_group_fn(EXISTING_GROUP), "w") as f:
        json.dump({
            r.GROUP_NAME_KEY: EXISTING_GROUP,
            r.GROUP_ITEMS_KEY: ["Existing Item"]
        }, f)


def _wipe_all():
    _wipe_added_blocks()


@pytest.fixture
def app():
    app = create_app({"TESTING": True})
    return app


@pytest.fixture
def client(app):
    return app.test_client()


@pytest.fixture(autouse=True)
def change_directory(monkeypatch):
    monkeypatch.chdir("testing_resources/")


@pytest.fixture(autouse=True)
def teardown():
    yield
    _wipe_added_blocks()
    # Get group name.
    try:
        os.remove(r.get_group_fn(NEW_GROUP))
    except FileNotFoundError:
        # As we're cleaning up we don't care if these files don't exist.
        pass

import json

import pytest

import populate_info.resources as r
from populate_info import create_app


def _wipe_added_blocks():
    with open(r.ADDED_ITEM_FN, "w") as f:
        json.dump({r.ITEM_LIST_KEY: []}, f)


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


@pytest.fixture
def teardown():
    yield
    _wipe_added_blocks()

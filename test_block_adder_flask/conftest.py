import json

import pytest

import block_adder_flask.resources as r


def _wipe_added_blocks():
    with open(r.ADDED_BLOCK_FN, "w") as f:
        json.dump({r.BLOCK_LIST_KEY: []}, f)


@pytest.fixture(autouse=True)
def change_directory(monkeypatch):
    monkeypatch.chdir("testing_resources/")


@pytest.fixture
def teardown():
    yield
    _wipe_added_blocks()

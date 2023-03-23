import json
from pathlib import Path

import pytest

import populate_info.resources as r
from populate_info import create_app

EXISTING_GROUP = "Test Group"
MISSING_GROUP = "Missing Group"
# TODO: delete the above and only use the below.
GROUP_1 = "Test Group 1"
GROUP_2 = "Test Group 2"
GROUP_3 = "Test Group 3"
ITEM_1 = "Test Item 1"
ITEM_2 = "Test Item 2"
ITEM_3 = "Test Item 3"


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
    _wipe_existing_group()


def _create_file(filename, data):
    print(f"filename {filename}")
    with open(filename, "w") as f:
        json.dump(data, f)


@pytest.fixture
def app():
    app = create_app({"TESTING": True})
    return app


@pytest.fixture
def client(app):
    return app.test_client()


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


@pytest.fixture(autouse=True)
def create_tmp_dir(monkeypatch, tmp_path):
    Path(tmp_path / r.DIR).mkdir(parents=True)
    Path(tmp_path / r.DIR / "groups").mkdir(parents=True)
    # Monkeypatch these paths before creating any files.
    monkeypatch.chdir(tmp_path)
    _create_file(r.ADDED_ITEM_FN, {r.ITEM_LIST_KEY: []})
    _create_file(r.FULL_ITEMS_LIST_FN, {r.ITEM_LIST_KEY: [ITEM_1, ITEM_2, ITEM_3]})

# @pytest.fixture(autouse=True)
# def change_directory(monkeypatch):
#     # TODO: delete this once I have switched to fully using tmp files.
#     monkeypatch.chdir("testing_resources/")

#
# @pytest.fixture(autouse=True)
# def teardown():
#     # TODO: delete this once I have switched to using temp files fully!
#     yield
#     _wipe_all()
#     # Get group name.
#     try:
#         os.remove(r.get_group_fn(GROUP_1))
#     except FileNotFoundError:
#         # As we're cleaning up we don't care if these files don't exist.
#         pass

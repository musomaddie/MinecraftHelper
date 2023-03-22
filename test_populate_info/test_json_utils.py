import json

import populate_info.resources as r
from populate_info import json_utils


def _added_item_file_contents():
    with open(r.ADDED_ITEM_FN) as f:
        return json.load(f)


# ################################### get_next_block tests ##################################
def test_get_next_item_first_item(teardown):
    assert json_utils.get_next_item() == "A Item"


def test_get_next_item_has_items(teardown):
    with open(r.ADDED_ITEM_FN, "w") as f:
        json.dump({r.ITEM_LIST_KEY: ["A Item"]}, f)
    assert json_utils.get_next_item() == "Second Item"


def test_get_next_item_no_items_left(teardown):
    with open(r.ADDED_ITEM_FN, "w") as f:
        json.dump({r.ITEM_LIST_KEY: [
            "A Item",
            "Second Item",
            "Yet Another Item"]}, f)
    assert json_utils.get_next_item() is None

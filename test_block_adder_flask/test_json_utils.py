import json

import block_adder_flask.resources as r
from block_adder_flask import json_utils


def _added_block_file_contents():
    with open(r.ADDED_BLOCK_FN) as f:
        return json.load(f)


# ################################### get_next_block tests ##################################
def test_get_next_block_first_block(teardown):
    assert json_utils.get_next_block() == "A Item"


def test_get_next_block_has_blocks(teardown):
    with open(r.ADDED_BLOCK_FN, "w") as f:
        json.dump({r.BLOCK_LIST_KEY: ["A Item"]}, f)
    assert json_utils.get_next_block() == "Second Item"


def test_get_next_block_no_blocks_left(teardown):
    with open(r.ADDED_BLOCK_FN, "w") as f:
        json.dump({r.BLOCK_LIST_KEY: [
            "A Item",
            "Second Item",
            "Yet Another Item"]}, f)
    assert json_utils.get_next_block() is None

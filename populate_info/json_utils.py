import json

import populate_info.resources as r


def load_json_from_file(filename: str) -> dict:
    with open(filename) as f:
        return json.load(f)


def get_next_item() -> str:
    """:return: name of next unpopulated block or item. """
    current_items = load_json_from_file(r.ADDED_ITEM_FN)[r.ITEM_LIST_KEY]
    all_items = load_json_from_file(r.FULL_ITEMS_LIST_FN)[r.ITEM_LIST_KEY]

    if len(current_items) >= len(all_items):
        return None

    return all_items[len(current_items)]

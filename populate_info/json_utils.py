import json
from os import path

import populate_info.resources as r


def add_to_group_file(group_name: str, item_name: str):
    if group_name == "" or group_name is None:
        return
    filename = r.get_group_fn(group_name)
    data = (load_json_from_file(filename)
            if path.exists(filename)
            else {r.GROUP_NAME_KEY: group_name, r.GROUP_ITEMS_KEY: []})
    data[r.GROUP_ITEMS_KEY].append(item_name)
    print(data)
    write_json_to_file(filename, data)


def write_json_to_file(filename: str, data: dict):
    with open(filename, "w") as f:
        json.dump(data, f)


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

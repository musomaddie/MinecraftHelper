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
    write_json_to_file(filename, data)


def remove_from_group_file(group_name: str, item_name: str):
    filename = r.get_group_fn(group_name)
    if not path.exists(filename):
        return
    data = load_json_from_file(filename)
    try:
        data[r.GROUP_ITEMS_KEY].remove(item_name)
    except ValueError:
        # If it doesn't exist the file will be unchanged so there is no point us modifying it further.
        return
    # TODO: consider deleting file completely if there are no items left.
    write_json_to_file(filename, data)


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


def write_json_category_to_file(item_name: str, group_name: str, category_name: str, category_info: dict):
    # TODO: implement for when there should be multiple things in this category.

    # try and load data if it already exists.
    filename = r.get_item_fn(item_name)
    data = {r.ITEM_NAME_KEY: item_name}
    # TODO - exclude group name better but results in circular import.
    if not (group_name is None or group_name == ""):
        data[r.GROUP_NAME_KEY] = group_name
    if path.exists(filename):
        data = load_json_from_file(filename)

    data[category_name] = category_info
    write_json_to_file(filename, data)


def write_json_to_file(filename: str, data: dict):
    with open(filename, "w") as f:
        json.dump(data, f)

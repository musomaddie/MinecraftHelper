import os
from os.path import isfile, join

from block_adder_flask.json_utils import get_file_contents, update_json_file

JSON_DIR = "block_adder_flask/item_information"


class AlreadyEnteredGroupInformation:

    group_name: str
    current_item: str
    other_items: list[str]
    should_show: bool
    other_item_info: dict

    def __init__(self, group_name, current_item):
        self.group_name = group_name
        self.current_item = current_item
        self.other_items = self._get_group_items()
        self.should_show = len(self.other_items) > 0
        self.other_item_info = (get_file_contents(f"{JSON_DIR}/{self.other_items[0]}.json")
                                if self.should_show else {})

    def _get_group_items(self):
        if self.group_name is None or self.group_name == "" or self.group_name == "None":
            return []
        item_list = get_file_contents(f"{JSON_DIR}/groups/{self.group_name}.json")["items"]
        item_list.remove(self.current_item)
        return item_list

    def get_obtaining_methods(self):
        if not self.should_show:
            return []
        obs = list(self.other_item_info.keys())
        obs.remove("name")
        obs.remove("group")
        return obs


def _get_different_item_from_group(group_name, current_item):
    for item in get_file_contents(f"{JSON_DIR}/groups/{group_name}.json")["items"]:
        if item != current_item:
            return item


def get_obtaining_methods_in_group(group_name, current_item):
    other_item_data = get_file_contents(
        f"{JSON_DIR}/{_get_different_item_from_group(group_name, current_item)}")
    keys = list(other_item_data.keys())
    keys.remove("name")
    keys.remove("group")
    return keys


def remove_from_group(group_name, item_name):
    if group_name == "" or group_name is None:
        return
    group_fn_full = f"{JSON_DIR}/groups/{group_name}.json"
    existing_group_info = get_file_contents(group_fn_full)
    existing_group_info["items"].remove(item_name)
    if len(existing_group_info["items"]) == 0:
        os.remove(group_fn_full)
    else:
        update_json_file(existing_group_info, group_fn_full)


def save_to_group(group_name, item_name):
    if group_name == "" or group_name is None:
        return
    group_dir = f"{JSON_DIR}/groups"
    group_fn_full = f"{group_dir}/{group_name}.json"
    if isfile(join(group_dir, group_name)):
        existing_group_items = get_file_contents(group_fn_full)
        if item_name not in existing_group_items["items"]:
            existing_group_items["items"].append(item_name)
            update_json_file(existing_group_items, group_fn_full)
    else:
        group_items = {"group name": group_name, "items": [item_name]}
        update_json_file(group_items, group_fn_full)


def get_updated_group_name(from_db: str, json_data: dict) -> str:
    if "group" in json_data:
        return json_data["group"]
    if from_db is None:
        return ""
    return from_db

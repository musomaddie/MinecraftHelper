import os
from os.path import isfile, join

from flask import Blueprint

from block_adder_flask.json_utils import get_file_contents, update_json_file

JSON_DIR = "block_adder_flask/item_information"

ALL_OBTAINMENT_METHODS = ["breaking",
                          "breaking other",
                          "crafting",
                          "trading"
                          "generated in chests", "generated in biome",
                          "generated as part of structure",
                          "post generation",
                          "stonecutter"]

bp = Blueprint("group_info", __name__)


class GroupInfoBuilder:
    group_name: str
    current_item: str
    other_items: list[str]
    should_show: bool
    other_item_info: dict

    def __init__(self, group_name: str, current_item: str) -> None:
        self.group_name = group_name
        self.current_item = current_item
        self.other_items = []
        self.should_show = False
        self.other_item_info = {}

    def build(self) -> 'AlreadyEnteredGroupInformation':
        return AlreadyEnteredGroupInformation(
            self.group_name,
            self.current_item,
            self.other_items,
            self.should_show,
            self.other_item_info)

    def set_other_items(self, other_items: list):
        self.other_items = other_items

    def set_should_show(self, should_show: bool):
        self.should_show = should_show

    def set_other_item_info(self, other_item_info: dict):
        self.other_item_info = other_item_info


class AlreadyEnteredGroupInformation:

    group_name: str
    current_item: str
    other_items: list[str]
    should_show: bool
    other_item_info: dict

    def __init__(self, group_name, current_item, other_items, should_show, other_item_info):
        self.group_name = group_name
        self.current_item = current_item
        self.other_items = other_items
        self.should_show = should_show
        self.other_item_info = other_item_info

    def get_obtaining_methods(self):
        if not self.should_show:
            return []
        key_list = list(self.other_item_info.keys())
        key_list.remove("name")
        key_list.remove("group")
        return key_list

    @staticmethod
    def get_group_items(group_name, current_item):
        item_list = get_file_contents(f"{JSON_DIR}/groups/{group_name}.json")["items"]
        item_list.remove(current_item)
        return item_list

    @staticmethod
    def create_first_time(group_name: str, current_item: str) -> 'AlreadyEnteredGroupInformation':
        builder = GroupInfoBuilder(group_name, current_item)
        if group_name is None or group_name == "" or group_name == "None":
            return builder.build()
        print(group_name)
        builder.set_other_items(
            AlreadyEnteredGroupInformation.get_group_items(group_name, current_item))
        builder.set_should_show(len(builder.other_items) > 0)
        builder.set_other_item_info(
            {} if len(builder.other_items) == 0
            else get_file_contents(f"{JSON_DIR}/{builder.other_items[0]}.json"))
        return builder.build()

    @staticmethod
    def create_from_dict(d: dict) -> 'AlreadyEnteredGroupInformation':
        builder = GroupInfoBuilder(d["group_name"], d["current_item"])
        builder.set_should_show(d["should_show"])
        builder.set_other_items(d["other_items"])
        builder.set_other_item_info(d["other_item_info"])
        return builder.build()


@bp.route("/obtaining", methods=["GET"])
def get_preexisting_obtaining_methods():
    return ["breaking_checkbox", "trading_checkbox"]
    # if "group_info" in session:
    #     return AlreadyEnteredGroupInformation.create_from_dict(
    #         session["group_info"]).get_obtaining_methods()
    # return []


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

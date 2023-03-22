import os
from os.path import isfile

from flask import Blueprint, session

from block_adder_flask.json_utils import get_file_contents, update_json_file

JSON_DIR = "block_adder_flask/item_information"

OBTAINMENT_METHODS_TITLE_TO_IDS = {
    "breaking": "breaking_checkbox",
    "breaking other": "breaking_other_checkbox",
    "crafting": "crafting_checkbox",
    "fishing": "fishing_checkbox",
    "trading": "trading_checkbox",
    "generated as part of structure": "nat_struct_checkbox",
    "post generation": "post_gen_checkbox",
    "stonecutter": "stonecutter_checkbox"
}

bp = Blueprint("group_info", __name__)


class GroupInfoBuilder:
    group_name: str
    current_item: str
    other_items: list[str]
    should_show: bool
    other_item_info: dict
    use_group_items: bool

    def __init__(self, group_name: str, current_item: str) -> None:
        self.group_name = group_name
        self.current_item = current_item
        self.other_items = []
        self.should_show = False
        self.other_item_info = {}
        self.use_group_items = False

    def build(self) -> 'ExistingGroupInfo':
        return ExistingGroupInfo(
            self.group_name,
            self.current_item,
            self.other_items,
            self.should_show,
            self.other_item_info,
            self.use_group_items
        )

    def set_other_items(self, other_items: list):
        self.other_items = other_items

    def set_should_show(self, should_show: bool):
        self.should_show = should_show

    def set_other_item_info(self, other_item_info: dict):
        self.other_item_info = other_item_info

    def set_use_group_items(self, use_group_items):
        self.use_group_items = use_group_items


class ExistingGroupInfo:
    group_name: str
    current_item: str
    other_items: list[str]
    should_show: bool
    other_item_info: dict
    use_group_items: bool

    def __init__(
            self,
            group_name,
            current_item,
            other_items,
            should_show,
            other_item_info,
            use_group_items):
        self.group_name = group_name
        self.current_item = current_item
        self.other_items = other_items
        self.should_show = should_show
        self.other_item_info = other_item_info
        self.use_group_items = use_group_items
        self.update_group_in_session()

    def __str__(self):
        return f"{self.group_name} (name), {self.current_item} (current item), {self.other_items} (items) {self.should_show} (ss)"

    def use_values_button_clicked(self, should_use_group: bool):
        if not self.should_show:
            return
        self.use_group_items = should_use_group
        self.update_group_in_session()

    def get_obtaining_methods(self):
        if self.should_show and self.use_group_items:
            key_list = list(self.other_item_info.keys())
            key_list.remove("name")
            key_list.remove("group")
            return [OBTAINMENT_METHODS_TITLE_TO_IDS[key] for key in key_list]
        return []

    def get_breaking_info(self):
        # TODO: handle case where there is multiple breaking options!! -> i.e. the dictionary is
        #  a list
        if self.should_show and self.use_group_items:
            if "breaking" not in self.other_item_info:
                return []

            og_item_info = self.other_item_info["breaking"]
            default_checked = [
                "requires_tool_any" if og_item_info["requires tool"] else "requires_tool_no",
                "requires_silk" if og_item_info["requires silk"] else "requires_silk_no"
            ]
            select_default = {}

            if "required tool" in og_item_info:
                select_default["spec_tool_select"] = og_item_info["required tool"]
            if "fastest tool" in og_item_info:
                default_checked.append("fastest_yes")
                select_default["fastest_tool"] = og_item_info["fastest tool"]

            # TODO: return a value indicating what button should be clicked.
            return {
                "default_checked_ids": default_checked,
                "select_default": select_default
            }

        return []

    def update_group_in_session(self):
        session["group_info"] = self.__dict__
        session["group_name"] = self.group_name

    @staticmethod
    def get_group_items(group_name, current_item):
        item_list = get_file_contents(f"{JSON_DIR}/groups/{group_name}.json")["items"]
        item_list.remove(current_item)
        return item_list

    @staticmethod
    def load_from_session(group_name: str, item_name: str) -> 'ExistingGroupInfo':
        print("reached here before breaking!")
        if "group_info" in session:
            existing = session["group_info"]
            if item_name == existing["current_item"] and group_name == existing["group_name"]:
                return ExistingGroupInfo.create_from_dict(session["group_info"])
        return ExistingGroupInfo.create_first_time(group_name, item_name)

    @staticmethod
    def create_first_time(group_name: str, current_item: str) -> 'ExistingGroupInfo':
        builder = GroupInfoBuilder(group_name, current_item)
        if group_name is None or group_name == "" or group_name == "None":
            return builder.build()
        builder.set_other_items(
            ExistingGroupInfo.get_group_items(group_name, current_item))
        builder.set_should_show(len(builder.other_items) > 0)
        builder.set_other_item_info(
            {} if len(builder.other_items) == 0
            else get_file_contents(f"{JSON_DIR}/{builder.other_items[0]}.json"))
        return builder.build()

    @staticmethod
    def create_from_dict(d: dict) -> 'ExistingGroupInfo':
        builder = GroupInfoBuilder(d["group_name"], d["current_item"])
        builder.set_should_show(d["should_show"])
        builder.set_other_items(d["other_items"])
        builder.set_other_item_info(d["other_item_info"])
        builder.set_use_group_items(d["use_group_items"])
        return builder.build()


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
    # TODO: don't save if group name and item name are the same??
    if group_name == "" or group_name is None:
        return
    group_dir = f"{JSON_DIR}/groups"
    group_fn_full = f"{group_dir}/{group_name}.json"
    if isfile(group_fn_full):
        # TODO: make sure this doesn't delete the existing group data.
        existing_group_items = get_file_contents(group_fn_full)
        print(existing_group_items)
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

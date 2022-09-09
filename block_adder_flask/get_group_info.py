from os.path import isfile, join

from block_adder_flask.json_utils import get_file_contents, update_json_file

JSON_DIR = "block_adder_flask/item_information"


def get_updated_group_name(from_db: str, json_data: dict) -> str:
    if "group" in json_data:
        return json_data["group"]
    if from_db is None:
        return ""
    return from_db


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


def should_show_group_button(group_name, this_item_name):
    if group_name is None or group_name == "" or group_name == "None":
        return False
    group_items = get_file_contents(f"{JSON_DIR}/{group_name}.json")["items"]
    return len(group_items) > 1

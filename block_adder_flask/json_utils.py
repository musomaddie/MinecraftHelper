import json

JSON_ITEM_LIST = "block_adder_flask/item_information/item_list.json"
JSON_DIR = "block_adder_flask/item_information"


def append_json_file(future_key: str, key_value_condition: list, filename: str):
    current_content = get_file_contents(filename)
    json_dict = {}
    for option in key_value_condition:
        # This should be added to the json file if there are only two values (key - value pair)
        # or if the third (optional) value is true.
        if len(option) == 2 or option[2]:
            json_dict[option[0]] = option[1]
    if future_key in current_content:
        if type(current_content[future_key]) != list:
            current_content[future_key] = [current_content[future_key]]
        current_content[future_key].append(json_dict)
    else:
        current_content[future_key] = json_dict
    update_json_file(current_content, filename)


def get_all_items_json_file(filename=JSON_ITEM_LIST):
    with open(filename) as f:
        return json.load(f)["items"]


def get_file_contents(filename: str):
    with open(filename) as f:
        return json.load(f)


def update_json_file(value: dict, filename: str):
    with open(filename, "w") as f:
        json.dump(value, f, indent=2)

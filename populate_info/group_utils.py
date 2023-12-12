import populate_info.resources as r
from populate_info.json_utils import (
    add_to_group_file, load_json_from_file, remove_from_group_file, write_json_category_to_file_given_filename,
    write_json_to_file)


def _get_group_info_for_category(group_name: str, category_key: str) -> dict:
    """ Helper to get group information for a given category. Private so that other callers don't have to know the
    correct key. """
    if not should_show_group(group_name):
        return {}
    return load_json_from_file(r.get_group_fn(group_name))[category_key]


def _group_already_has_info(group_name: str, category_name: str, category_info: dict) -> bool:
    """
    Returns true iff there already exists the given category info for the given category name in the given group.

    :param group_name:
    :param category_name:
    :param category_info:
    :return:
    """
    # TODO - handle the group key just not existing
    existing_group_cat_info = _get_group_info_for_category(group_name, category_name)
    if type(existing_group_cat_info) == dict:
        return existing_group_cat_info == category_info
    elif type(existing_group_cat_info) == list:
        return category_info in existing_group_cat_info
    return False


def _replace_placeholder(replace_name: str, data: dict) -> dict:
    """ Replaces the placeholder in dictionary items with the given name.

    Returns the dictionary even though it is modified in place for easier call chaining."""
    # Try slots
    if isinstance(data, list):
        return [_replace_placeholder(replace_name, item) for item in data]
    for key, value in data.get("slots", {}).items():
        if "<PLACEHOLDER>" in value:
            data.get("slots")[key] = value.replace("<PLACEHOLDER>", replace_name)

    return data


def _remove_shared_part(name_1: str, name_2: str) -> str:
    """ Removes any words from name_1 that are also present in name 2. Raises a ValueError if there are no shared
    elements.
    """
    words_1 = name_1.split(" ")
    words_2 = name_2.split(" ")
    result = [word for word in words_1 if word not in words_2]
    if len(result) == 0:
        raise ValueError(f"{name_1} is identical to {name_2}.")
    return " ".join(result)


def _maybe_generalise_category_info(group_name: str, current_item_name: str, category_key, category_info: dict) -> None:
    """
    Generalises any relevant information within the passed category_info. Information is generalised inplace.

    For information to be generalised the following conditions must be met.
        - there are other item names within the category_info (determined through the category key and info)
        - the other item names shares at least one word with the current name that is not present within the group name.
    """
    category_keys_to_possible_items = {"crafting": ["slots"]}
    if category_key not in category_keys_to_possible_items:
        return

    # Calculate the interesting part before continuing, so it can be calculated outside the for loop, and return
    # early if the item does not have any words in common with the group.
    unique_item_word = _remove_shared_part(current_item_name, group_name)
    if len(unique_item_word) == len(current_item_name):
        return

    for possible_item_key in category_keys_to_possible_items[category_key]:
        # TODO: handle other types of category_info, not just dicts.
        for item_key in category_info[possible_item_key]:
            if unique_item_word in category_info[possible_item_key][item_key]:
                category_info[possible_item_key][item_key] = category_info.get(possible_item_key).get(
                    item_key).replace(unique_item_word, "<PLACEHOLDER>")


def add_to_group(group_name: str, item_name: str):
    """
    Adds the item to the given group.
    """
    # Exit early if the group name isn't interesting, otherwise add it to the json file.
    if not is_group_name_interesting(group_name):
        return
    add_to_group_file(group_name, item_name)


def get_next_group_data(group_data, item_data) -> dict:
    if type(group_data) == dict:
        return group_data
    if type(item_data) == dict:
        return group_data[0 if len(item_data) == 0 else 1]
    return group_data[len(item_data)]


def get_button_choice(group_data, item_data) -> str:
    if type(group_data) == dict:
        return "next"
    expected_number = len(group_data)
    current_number = 1 if type(item_data) == dict else len(item_data)
    return "another" if current_number < expected_number - 1 else "next"


def get_group_info(group_name: str, item_name: str, category_key: str) -> dict[str: str]:
    """ Returns all the group information for the given group. """
    # TODO: update tests for placeholder
    return _replace_placeholder(
        _remove_shared_part(item_name, group_name),
        _get_group_info_for_category(group_name, category_key)
    )


# TODO: for group info with more than one item in it introduce a skip button to not save it but instead move to next
#  item.

def get_group_categories(group_name: str) -> list[str]:
    """ The group will have the information saved in the json for ease of use, so I just have to find and return it."""
    if not should_show_group(group_name):
        return []
    data = load_json_from_file(r.get_group_fn(group_name))
    # Get all the keys of data without item name and item list.
    return [key for key in list(data.keys()) if key != r.GROUP_NAME_KEY and key != r.GROUP_ITEMS_KEY]


def include_group_in_item_file(group_name: str, item_data: dict[str, str]):
    if not is_group_name_interesting(group_name):
        return
    item_data[r.GROUP_NAME_KEY] = group_name


def is_group_name_interesting(group_name: str) -> bool:
    """
    Returns whether the group name is 'interesting'. (used to exit early).

    :param group_name:
    :return: true iff group name is not none or ""
    """
    return group_name is not None and group_name != ""


def load_group_items(group_name: str) -> list[str]:
    """ Returns a list of all items in the provided group."""
    return load_json_from_file(r.get_group_fn(group_name))[r.GROUP_ITEMS_KEY]


def maybe_group_toggle_update_saved(session, request_form: dict) -> bool:
    """ Updates the status of the 'use group' toggle if it has been changed.

     Returns true if the toggle has changed, false otherwise. (to help control data flow).
     :param session: """
    if "update-use-group-values" in request_form:
        # if we've been told to update it we need to use the value passed to set this value (because who knows how
        # many times it's been toggled?!)
        session[r.USE_GROUP_VALUES_SK] = "group-checkbox" in request_form
        return True
    return False


def maybe_write_category_to_group(group_name: str, item_name: str, category_name: str, category_info: dict):
    """ Writes information about this category to the group file if the group name is interesting, and will generalise
    information within the category if appropriate. (generalised information will contain "<PLACEHOLDER>" where item
    specific information would otherwise live).
    """
    if not is_group_name_interesting(group_name):
        return
    if _group_already_has_info(group_name, category_name, category_info):
        return
    _maybe_generalise_category_info(group_name, item_name, category_name, category_info)
    write_json_category_to_file_given_filename(
        r.get_group_fn(group_name), category_name, category_info
    )


def should_show_group(group_name: str):
    """ Returns true if values should be autopopulated from this group.

    This is true when the group name is interesting and there is another item in it."""
    if not is_group_name_interesting(group_name):
        return False
    return len(load_group_items(group_name)) > 1


def update_group(old_group_name, new_group_name, item_name):
    """
    Moves the given item from the old group to the new group.

    :param old_group_name:
    :param new_group_name:
    :param item_name:
    """
    remove_from_group_file(old_group_name, item_name)
    add_to_group(new_group_name, item_name)


def remove_from_group(group_name: str, item_name: str):
    """
    Removes the given item from the given group.

    :param group_name:
    :param item_name:
    """
    if not is_group_name_interesting(group_name):
        remove_from_group_file(group_name, item_name)


def write_group_name_to_item_json(item_name: str, group_name: str):
    """ Write the name of this group to the item file. """
    if not is_group_name_interesting(group_name):
        return
    data = load_json_from_file(r.get_item_fn(item_name))
    data[r.GROUP_NAME_KEY] = group_name
    write_json_to_file(r.get_item_fn(item_name), data)

import populate_info.resources as r
from populate_info.json_utils import (add_to_group_file, load_json_from_file, remove_from_group_file,
    write_json_to_file,
    write_json_category_to_file_given_filename)


def add_to_group(group_name: str, item_name: str):
    """
    Adds the item to the given group.

    :param group_name:
    :param item_name:
    """
    # Exit early if the group name isn't interesting, otherwise add it to the json file.
    if not is_group_name_interesting(group_name):
        return
    add_to_group_file(group_name, item_name)


def get_group_breaking_info(group_name: str) -> dict[str: str]:
    """ Gets all the breaking information from the existing group. """
    if not should_show_group(group_name):
        return {}
    return load_json_from_file(r.get_group_fn(group_name))[r.BREAKING_CAT_KEY]


def get_group_crafting_info(group_name: str) -> dict[str: str]:
    """ Gets all the crafting information from the existing group. """
    if not should_show_group(group_name):
        return {}
    return load_json_from_file(r.get_group_fn(group_name))[r.CRAFTING_CAT_KEY]


def get_group_categories(group_name: str) -> list[str]:
    """ The group will have the information saved in the json for convinnce, so I just have to find and return it."""
    if not should_show_group(group_name):
        return []
    data = load_json_from_file(r.get_group_fn(group_name))
    # Get all the keys of data without item name and item list.
    keys = list(data.keys())
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
    if "update_use_group_values" in request_form:
        # if we've been told to update it we need to use the value passed to set this value (because who knows how
        # many times it's been toggled?!)
        session[r.USE_GROUP_VALUES_SK] = "group_checkbox" not in request_form
        return True
    return False


def maybe_write_category_to_group(group_name: str, category_name: str, category_info: dict):
    """ Writes information about this category to the group file if the group name is interesting. """
    if not is_group_name_interesting(group_name):
        return
    write_json_category_to_file_given_filename(
        r.get_group_fn(group_name), category_name, category_info
    )


def should_show_group(group_name: str):
    """ Returns true if values should be auto-populated from this group.

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


def write_group_data_to_json(item_name: str, group_name: str):
    """ Write the name of this group to the item file. """
    if not is_group_name_interesting(group_name):
        return
    data = load_json_from_file(r.get_item_fn(item_name))
    data[r.GROUP_NAME_KEY] = group_name
    write_json_to_file(r.get_item_fn(item_name), data)

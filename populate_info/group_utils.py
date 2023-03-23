from populate_info.json_utils import add_to_group_file


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


def is_group_name_interesting(group_name: str) -> bool:
    """
    Returns whether the group name is 'interesting'. (used to exit early).

    :param group_name:
    :return: true iff group name is not none or ""
    """
    return group_name is not None and group_name != ""


def update_group(old_group_name, new_group_name, item_name):
    pass
    # remove_from_group(old_group_name, item_name)
    # add_to_group(new_group_name, item_name)


def remove_from_group(group_name: str, item_name: str):
    """
    Removes the given item from the given group.

    :param group_name:
    :param item_name:
    """
    if not is_group_name_interesting(group_name):
        remove_from_group_file(group_name, item_name)

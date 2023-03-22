def add_to_group(group_name: str, item_name: str):
    """
    Adds the item to the given group.

    :param group_name:
    :param item_name:
    """
    if group_name == "" or group_name is None:
        return
    # Otherwise add to json.
    add_to_group_file(group_name, item_name)
    pass


def update_group(old_group_name, new_group_name, item_name):
    pass
    # remove_from_group(old_group_name, item_name)
    # add_to_group(new_group_name, item_name)

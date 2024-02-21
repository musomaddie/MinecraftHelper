""" Factory for creating item instances. """
from populate_info.item.item import Item
from populate_info.item_group import group_factory
from populate_info.item_group.group import Group
from populate_info.item_group.group_parser import GroupJsonParser


def create(item_name: str) -> Item:
    """ Creates an item with the corresponding name, but not an interesting group. """
    group = group_factory.create("", item_name)
    return Item(item_name, group)


def create_with_group(item_name: str, group_name: str) -> Item:
    """ Creates an item with the corresponding name and an interesting group. """
    group = group_factory.create(group_name, item_name)
    return Item(item_name, group)


def create_from_dictionary(item_dict: dict) -> Item:
    """ Creates an item from the given dictionary. """
    group_dict = item_dict["group"]
    parser = GroupJsonParser(group_dict["name"])
    group = Group(
        name=group_dict["name"],
        item_names=group_dict["item_names"],
        current_item=group_dict["current_item"],
        is_interesting=group_dict["is_interesting"],
        json_parser=parser,
        use_group_values=group_dict["use_group_values"]
    )
    return Item(item_dict["name"], group)

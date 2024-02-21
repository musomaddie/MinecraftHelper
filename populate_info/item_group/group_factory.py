""" Factory for creating group instances. """
from populate_info.item_group.group import Group
from populate_info.item_group.group_parser import GroupJsonParser


def create(
        group_name: str,
        item_name: str) -> Group:
    """ Crates a Group object from the given group and item name.

    In doing so, will parse a JSON file corresponding to the given group name, if it exists.
    """
    parser = GroupJsonParser(group_name)

    return Group(
        name=group_name,
        item_names=parser.get_all_items(),
        current_item=item_name,
        is_interesting=len(parser.get_all_items()) > 0,
        json_parser=parser,
    )

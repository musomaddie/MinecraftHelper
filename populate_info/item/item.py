""" A class for an individual minecraft item or block. """
from dataclasses import dataclass

from dataclasses_json import dataclass_json

# TODO -> clean up this import statement its kinda gross.
from populate_info.item_group.group import Group


@dataclass_json
@dataclass
class Item:
    """ A minecraft item or block. """
    name: str
    group: Group

    def get_url(self):
        """ Returns the url for this item on the Minecraft Wiki. """
        return f"https://minecraft.fandom.com/wiki/{self.name.replace(' ', '%20')}"

    def change_group(self, new_group_name):
        """ Removes this item from the current group, and adds it to the new group name."""
        pass

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
        # TODO -> insert link to wiki here!
        pass

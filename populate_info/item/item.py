""" A class for an individual minecraft item or block. """
import json
from dataclasses import dataclass

from dataclasses_json import dataclass_json

from populate_info.item_group import group_factory
# TODO -> clean up this import statement its kinda gross.
from populate_info.item_group.group import Group

DIR = "populate_info/item_data/"


@dataclass_json
@dataclass
class Item:
    """ A minecraft item or block. """
    name: str
    group: Group

    def _filename(self) -> str:
        """ Returns the filename of this item"""
        return f"{DIR}{self.name.replace(' ', '_').lower()}.json"

    def get_url(self) -> str:
        """ Returns the url for this item on the Minecraft Wiki. """
        return f"https://minecraft.fandom.com/wiki/{self.name.replace(' ', '%20')}"

    def change_group(self, new_group_name):
        """ Changes the group associated with this item to the new one. """
        self.group = group_factory.create(group_name=new_group_name, item_name=self.name)

    def create_json_file(self):
        """ Creates a json file for this item. """
        json_data = {"item name": self.name, }
        # Only save the group name if it's actually interesting.
        if self.group.is_interesting:
            json_data["group name"] = self.group.name

        with open(self._filename(), "w") as f:
            json.dump({"item name": self.name}, f, indent=2)

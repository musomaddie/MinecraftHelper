""" methods for handling group json stuff. Can be called from multiple places. """
import json

from dataclasses import dataclass
from os import path

""" The file location where all the group json files are stored. """
GROUP_DIR = "populate_info/item_data/groups/"

""" Keys used within the JSON file. Saved as variables for sanity. """
KEY_GROUP_NAME = "group name"
KEY_ITEM_LIST = "items"
KEY_BREAKING = "breaking"


@dataclass
class GroupJsonParser:
    """ A middle ground between the group class and the json file. """

    group_name: str

    def _filename(self) -> str:
        """ Returns the filename corresponding to the group name of this. """
        return f"{GROUP_DIR}{self.group_name.lower().replace(' ', '_')}.json"

    def _create_file(self):
        """ Creates a file for this group. """
        with open(self._filename(), "w") as f:
            json.dump({"group name": self.group_name}, f, indent=2)

    def _write_all_contents(self, contents: dict):
        with open(self._filename(), "w") as f:
            json.dump(contents, f, indent=2)

    def get_file_contents(self) -> dict:
        """ Returns the contents of this JSON file as dict."""
        if not path.exists(self._filename()):
            return {}

        with open(self._filename()) as f:
            return json.load(f)

    def get_all_categories(self) -> list[str]:
        """ Returns all the categories that this group is populated by. """
        # The keys of the group's JSON (excluding group_name and items) will be the names of the categories.
        return [
            key for key in list(self.get_file_contents().keys()) if key != KEY_GROUP_NAME and key != KEY_ITEM_LIST
        ]

    def get_all_items(self):
        """ Returns all the items within this group. """
        return self.get_file_contents().get(KEY_ITEM_LIST, [])

    def write_items(self, group_items: list[str]):
        """ Adds the given item to the json file. """
        # If the file doesn't exist, create one.
        if not path.exists(self._filename()):
            self._create_file()

        existing_contents = self.get_file_contents()
        existing_contents[KEY_ITEM_LIST] = group_items
        self._write_all_contents(existing_contents)

    def get_breaking_data(self) -> list[dict]:
        """ Returns the breaking data for this group. """
        return self.get_file_contents().get(KEY_BREAKING, [])

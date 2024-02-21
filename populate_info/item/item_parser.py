""" middle ground between item class and item json. """
import json
from dataclasses import dataclass

DIR = "populate_info/item_data/"


@dataclass
class ItemJsonParser:
    """ Parsers information from the item class to / from the item json. """

    item_name: str

    def _filename(self) -> str:
        return f"{DIR}{self.item_name.replace(' ', '_').lower()}.json"

    def get_contents(self) -> dict:
        """ Returns the entire contents of this item's json. """
        with open(self._filename()) as f:
            return json.load(f)

    def write_initial_information(self, group_name: str):
        """ Writes the initial information to the json file. """
        json_data = {"item_name": self.item_name, }
        if group_name != "":
            json_data["group name"] = group_name

        with open(self._filename(), "w") as f:
            json.dump(json_data, f, indent=2)

    def get_breaking_info(self) -> list[dict]:
        """ Returns breaking information for this item. """
        return self.get_contents().get("breaking", [])

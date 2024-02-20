""" A group class. """
import json
from dataclasses import dataclass

from dataclasses_json import dataclass_json

from populate_info.item_data.categories.category import PopulationCategory

""" The file location where all the group json files are stored. """
GROUP_DIR = "populate_info/item_data/groups/"

""" Keys used within the JSON file. Saved as variables for sanity. """
KEY_GROUP_NAME = "group name"
KEY_ITEM_LIST = "items"


@dataclass_json
@dataclass
class Group:
    """ A group of related items.

    For the most part items in a group share mostly the same information.
    """
    name: str
    item_names: list[str]
    # Saved as strings instead of item types so the group can be saved in the flask session without much bloat

    is_interesting: bool

    def _filename(self) -> str:
        """ Returns the filename of this group's json file."""
        return f"{GROUP_DIR}{self.name.lower().replace(' ', '_')}.json"

    def _read_json(self) -> dict:
        """ Returns the contents of the corresponding JSON file for this group. See (TODO write the write method) for
        information about file structure."""
        with open(self._filename()) as f:
            return json.load(f)

    def should_show_group(self) -> bool:
        """ Returns true only if this group should be shown. """
        return self.is_interesting

    def categories_html_ids(self) -> list[str]:
        """ Returns a list of the html ids of all categories of which items in this group populate.

        Returns an empty list if the group isn't interesting.
        """
        if not self.is_interesting:
            return []

        def interesting_key(key):
            """ True if the key corresponds to a category name. """
            return key != KEY_GROUP_NAME and key != KEY_ITEM_LIST

        # The keys of the group's JSON (excluding group_name and items) will be the names of the categories.
        categories = [PopulationCategory(key) for key in list(self._read_json().keys()) if interesting_key(key)]
        return [category.html_id() for category in categories]

""" A group class. """
from dataclasses import dataclass

from dataclasses_json import dataclass_json

from populate_info.categories.category import PopulationCategory
from populate_info.item_group.group_parser import GroupJsonParser


@dataclass_json
@dataclass
class Group:
    """ A group of related items.

    For the most part items in a group share mostly the same information.
    """
    name: str
    item_names: list[str]
    # Saved as strings instead of item types so the group can be saved in the flask session without much bloat
    current_item: str
    is_interesting: bool
    json_parser: GroupJsonParser
    use_group_values: bool

    def should_show_group(self) -> bool:
        """ Returns true only if this group should be shown. """
        return self.is_interesting

    def categories_html_ids(self) -> list[str]:
        """ Returns a list of the html ids of all categories of which items in this group populate.

        Returns an empty list if the group isn't interesting.
        """
        categories = [
            PopulationCategory(category)
            for category in self.json_parser.get_all_categories()]
        return [category.html_id() for category in categories]

    def check_toggle_selected(self, request_data: dict) -> bool:
        """ Check if the toggle has been changed. Returns true if the toggle has changed."""
        if "update-use-group-values" in request_data:
            self.use_group_values = "group-checkbox" in request_data
            return True
        return False

    def add_current_item_to_json(self):
        """ Add the current item to the json file for this group. """
        # Don't bother writing to the file if the group is non-interesting.
        if not self.is_interesting:
            return
        self.item_names.append(self.current_item)
        self.json_parser.write_items(self.item_names)

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

    def should_show_group(self) -> bool:
        """ Returns true only if this group should be shown. """
        return self.is_interesting

    def remove_from_group(self, item_name: str):
        """ Removes the given item from this group.

        This method does not modify the JSON file, so changes to the group should only be made prior to any further
        processing of this item.
        """
        self.item_names.remove(item_name)

    def categories_html_ids(self) -> list[str]:
        """ Returns a list of the html ids of all categories of which items in this group populate.

        Returns an empty list if the group isn't interesting.
        """
        categories = [
            PopulationCategory(category)
            for category in self.json_parser.get_all_categories()]
        return [category.html_id() for category in categories]

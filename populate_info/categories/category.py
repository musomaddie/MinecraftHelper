""" Category dataclass. """
from dataclasses import dataclass

NAME_TO_HTML_ID = {
    "breaking": "breaking-cbox",
    "crafting": "crafting-cbox",
    "environment changes": "env-changes-cbox"
}


@dataclass
class PopulationCategory:
    """
    A population category - i.e. a particular way of obtaining an item.
    """
    name: str

    def html_id(self) -> str:
        """ Returns the html id corresponding to this category. """
        return NAME_TO_HTML_ID[self.name]

    @staticmethod
    def get_next_information(item_data: list[dict], group_data: list[dict]) -> dict:
        """ Returns the next information. Assumes it does exist. """
        current_data_idx = len(item_data)
        return group_data[current_data_idx]

    @staticmethod
    def has_more_information_afterwards(item_data: list[dict], group_data: list[dict]) -> bool:
        """ Returns true if there's another item that exists. """
        current_data_idx = len(item_data)
        return current_data_idx < len(group_data) - 1

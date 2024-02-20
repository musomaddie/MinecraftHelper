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

""" Common and shared code for the population pages (python flask). """
from abc import ABCMeta, abstractmethod
from dataclasses import dataclass

from flask import render_template, session

from populate_info.item import item_factory
from populate_info.item.item import Item


@dataclass
class PopulationPage(metaclass=ABCMeta):
    """ Super class for population pages. """
    item: Item

    def __init__(self):
        self.item = item_factory.create_from_dictionary(session["current_item"])

    @abstractmethod
    def json_to_html_ids(self):
        """
        Returns the html ids corresponding to the saved values within the json file.

        button-choice: [ another | next ] depending on whether there is more information.
        to-mark-checked: [ key1, key2 ] a list of checkboxes that should be marked.
        dropdown-selected [key1: value1, ...] key value pairs corresponding to html ids of drop down boxes,
        and their default selected option.
        """
        pass

    def render_population_template(
            self,
            template_name: str):
        """ 
        Renders the given template
        """
        return render_template(
            template_name,
            item_name=self.item.name,
            group_name=self.item.group.name,
            is_toggle_selected=self.item.group.use_group_values,
            group_info=self.json_to_html_ids(),
            show_group=self.item.group.should_show_group()
        )

    @staticmethod
    def idify_string(item: str) -> str:
        """ Inverse behaviour to clean_up_tool_name. """
        return item.lower().replace(" ", "-")

    @staticmethod
    def clean_up_string(item: str) -> str:
        """ Takes in a string and cleans it up for display. """
        return item.replace("-", " ").title()
    # data_to_populate = get_next_group_data(group_data, item_data)
    # result = {
    #     # always has requires tool and silk.
    #     "to-mark-checked": [
    #         REQ_TOOL_JSON_TO_HTML[data_to_populate[KEY_TOOL]],
    #         SILK_TOUCH_JSON_TO_HTML[data_to_populate[KEY_SILK_TOUCH]]
    #     ],
    #     "reveal": [],  # TODO - test this!!
    #     "button-choice": get_button_choice(group_data, item_data),
    #     "dropdown-select": {}
    # }
    # # Add the special cases
    # if data_to_populate[KEY_TOOL] == "specific":
    #     result["dropdown-select"]["specific-tool-select"] = r.idify_tool_name(
    #         data_to_populate[KEY_TOOL_SPECIFIC])
    #     result["reveal"].append("spec-tool-select")
    # # TODO - make sure to add a possible no key for the fastest silk.
    # if KEY_TOOL_FASTEST in data_to_populate:
    #     result["to-mark-checked"].append("fastest-tool-yes")
    #     result["dropdown-select"]["fastest-specific-tool-select"] = r.idify_tool_name(
    #         data_to_populate[KEY_TOOL_FASTEST])
    #     result["reveal"].append("fastest-specific-tool-select")
    # else:
    #     result["to-mark-checked"].append("fastest-tool-no")
    #
    # return result

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

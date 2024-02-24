""" A class for an individual minecraft item or block. """
import json
from dataclasses import dataclass

from dataclasses_json import dataclass_json
from flask import session, redirect, url_for

from populate_info.item.item_parser import ItemJsonParser
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
    parser: ItemJsonParser

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
        self.parser.write_initial_information(self.group.name)

    def move_to_next_category(self):
        """ Moves to the next category. """
        # If there isn't another category we instead move to the next item. There is no need to save these results,
        # this should happen prior to this call.
        if len(session["methods"]) == 0:
            return redirect(url_for("add.start_adding_item", item_name=self.get_next_item()))
        next_category = session["methods"].pop(0)
        # TODO -> do I need to reassign the session variable.
        return redirect(url_for(next_category, item_name=self.name))

    def get_item_breaking_data(self) -> list[dict]:
        """ Gets the breaking data associated with this item. """
        return self.parser.get_breaking_info()

    @staticmethod
    def get_next_item() -> str:
        """ The name of the next unpopulated block of item. """
        current_items = []
        all_items = []
        with open(f"{DIR}all_items/added_items.json") as f:
            current_items = json.load(f)["items"]
        with open(f"{DIR}all_items/full_item_list.json") as f:
            all_items = json.load(f)["items"]

        if len(current_items) >= len(all_items):
            return ""
        return all_items[len(current_items)]

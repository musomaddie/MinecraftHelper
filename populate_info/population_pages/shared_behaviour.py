""" Helper functions to avoid duplicate code.

TODO -> consider renaming this.
"""
from flask import render_template, session

import populate_info.resources as r
from populate_info.group_utils import should_show_group, get_group_info, maybe_write_category_to_group
from populate_info.json_utils import get_current_category_info, write_json_category_to_file


def render_population_template(
        template_name: str,
        item_name: str,
        group_name: str,
        category_key: str,
        json_to_html_ids,
):
    """ Renders the given template. """
    return render_template(
        template_name,
        item_name=item_name,
        group_name=group_name,
        is_toggle_selected=session.get(r.USE_GROUP_VALUES_SK, False),
        group_info=json_to_html_ids(
            get_group_info(group_name, item_name, category_key),
            get_current_category_info(item_name, category_key)),
        show_group=should_show_group(group_name)
    )


def save_values_to_file(
        item_name: str,
        category_key: str,
        data: dict):
    """ Saves the given item data to file (including possible group file). """
    write_json_category_to_file(item_name, category_key, data)
    # TODO (add to github too) - replace all session[] with session.get with default string.
    maybe_write_category_to_group(session.get(r.GROUP_NAME_SK, ""), item_name, category_key, data)

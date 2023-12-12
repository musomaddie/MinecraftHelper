""" Helper functions to avoid duplicate code.

TODO -> consider renaming this.
"""
from flask import render_template, session

import populate_info.resources as r
from populate_info.group_utils import should_show_group


def render_population_template(
        template_name: str,
        item_name: str,
        group_name: str,
        group_info: dict,
):
    """ Renders the given template. """
    return render_template(
        template_name,
        item_name=item_name,
        group_name=group_name,
        is_toggle_selected=session.get(r.USE_GROUP_VALUES_SK, False),
        group_info=group_info,
        show_group=should_show_group(group_name)
    )

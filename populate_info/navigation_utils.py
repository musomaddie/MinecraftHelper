from flask import redirect, session, url_for

import populate_info.resources as r
from populate_info.json_utils import get_next_item


def move_next_category(item_name: str):
    """ Moves to the next category. """
    if len(session[r.METHOD_LIST_SK]) == 0:
        return redirect(url_for("add.start_adding_item", item_name=get_next_item()))
    next_category = session[r.METHOD_LIST_SK].pop(0)
    session[r.METHOD_LIST_SK] = session[r.METHOD_LIST_SK]
    return redirect(url_for(next_category, item_name=item_name))


def either_move_next_category_or_repeat(item_name: str, current_category: str, request_form: dict[str: str]):
    """ Either reloads the page for the current category, or moves to the next one. """
    if "next" in request_form:
        return move_next_category(item_name)
    return redirect(url_for(current_category, item_name=item_name))

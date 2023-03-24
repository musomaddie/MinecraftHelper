from flask import redirect, url_for

from populate_info.json_utils import get_next_item


def move_next_category(item_name: str, categories: list[str]):
    """ Moves to the next category. """
    if len(categories) == 0:
        return redirect(url_for("add.start_adding_item", item_name=get_next_item()))
    next_category = categories.pop()
    return redirect(url_for(next_category, item_name=item_name))

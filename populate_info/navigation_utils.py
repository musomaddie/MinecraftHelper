from flask import redirect, url_for

from populate_info.json_utils import get_next_item


def move_next_category(item_name: str, categories: list[str]):
    """ Moves to the next category. """
    if len(categories) == 0:
        return redirect(url_for("add.start_adding_item", item_name=get_next_item()))
    next_category = categories.pop(0)
    return redirect(url_for(next_category, item_name=item_name))


def either_move_next_category_or_repeat(
        item_name: str, current_category: str, categories: list[str], request_form: dict[str: str]):
    """ Either reloads the page for the current category, or moves to the next one. """
    if "next" in request_form:
        return move_next_category(item_name, categories)
    return redirect(url_for(current_category, item_name=item_name))

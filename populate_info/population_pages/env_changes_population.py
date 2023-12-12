from flask import session, request, redirect, url_for

import populate_info.resources as r
from populate_info.group_utils import (
    maybe_group_toggle_update_saved, maybe_write_category_to_group, get_group_env_changes_info,
    get_button_choice, get_next_group_data)
from populate_info.json_utils import write_json_category_to_file, get_current_category_info
from populate_info.navigation_utils import either_move_next_category_or_repeat
from populate_info.population_pages import item_blueprint
from populate_info.population_pages.template_renderer import render_population_template


def env_changes_json_to_html_ids(
        group_data, current_item_data) -> dict:
    if len(group_data) == 0:
        return {}
    data_to_populate = get_next_group_data(group_data, current_item_data)
    return {"change-text": data_to_populate["change"],
            "button-choice": get_button_choice(group_data, current_item_data)}


@item_blueprint.route("/env_changes/<item_name>", methods=["GET", "POST"])
def env_changes(item_name):
    group_name = session.get(r.GROUP_NAME_SK, "")
    if request.method == "GET":
        return render_population_template(
            "add_item/env_changes.html",
            item_name=item_name,
            group_name=group_name,
            group_info=env_changes_json_to_html_ids(
                get_group_env_changes_info(group_name, item_name),
                get_current_category_info(item_name, r.ENV_CHANGES_CAT_KEY)),
        )

    if maybe_group_toggle_update_saved(session, request.form):
        return redirect(url_for("add.env_changes", item_name=item_name))

    # Save data
    data = {r.EC_CHANGE_J_KEY: request.form["change-text"]}
    # TODO: add dup check to individual file as well.
    write_json_category_to_file(item_name, r.ENV_CHANGES_CAT_KEY, data)
    maybe_write_category_to_group(session[r.GROUP_NAME_SK], item_name, r.ENV_CHANGES_CAT_KEY, data)

    return either_move_next_category_or_repeat(item_name, "add.env_changes", request.form)

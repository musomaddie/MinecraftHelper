from flask import session, request, redirect, url_for

import populate_info.resources as r
from populate_info.group_utils import (
    maybe_group_toggle_update_saved, get_button_choice, get_next_group_data)
from populate_info.navigation_utils import either_move_next_category_or_repeat
from populate_info.population_pages import item_blueprint
from populate_info.population_pages.shared_behaviour import render_population_template, save_values_to_file

KEY_CHANGE = "change"


def env_changes_json_to_html_ids(
        group_data, current_item_data) -> dict:
    if len(group_data) == 0:
        return {}
    data_to_populate = get_next_group_data(group_data, current_item_data)
    return {"change-text": data_to_populate["change"],
            "button-choice": get_button_choice(group_data, current_item_data)}


@item_blueprint.route("/env_changes/<item_name>", methods=["GET", "POST"])
def env_changes(item_name):
    group_name = session.get(r.SK_GROUP_NAME, "")
    if request.method == "GET":
        return render_population_template(
            "add_item/env_changes.html",
            item_name,
            group_name,
            r.CK_ENV_CHANGES,
            env_changes_json_to_html_ids)

    if maybe_group_toggle_update_saved(session, request.form):
        return redirect(url_for("add.env_changes", item_name=item_name))

    # Save data
    data = {KEY_CHANGE: request.form["change-text"]}
    # TODO: add dup check to individual file as well.
    save_values_to_file(item_name, r.CK_ENV_CHANGES, data)

    return either_move_next_category_or_repeat(item_name, "add.env_changes", request.form)

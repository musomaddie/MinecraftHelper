from flask import render_template, session, request, redirect, url_for

import populate_info.resources as r
from populate_info.group_utils import (maybe_group_toggle_update_saved, maybe_write_category_to_group,
    get_group_env_changes_info)
from populate_info.json_utils import write_json_category_to_file, get_current_category_info
from populate_info.navigation_utils import either_move_next_category_or_repeat
from populate_info.population_pages import item_blueprint


def env_changes_json_to_html_ids(
        json_data, current_item_data) -> dict:
    # TODO - make sure to (eventually) handle calls that misalign with the group expectations.
    print(json_data)
    print(current_item_data)
    if type(json_data) == dict:
        # TODO: still probs check counting here.
        return {"change_text": json_data["change"], "button_choice": "next"}
    # The JSON_DATA is a list
    expected_number = len(json_data)
    current_number = 1 if type(current_item_data) == dict else len(current_item_data)
    print(current_number)
    print(expected_number)
    return {"change_text": json_data[current_number]["change"],
            "button_choice": "another" if current_number < expected_number - 1 else "next"}


@item_blueprint.route("/env_changes/<item_name>", methods=["GET", "POST"])
def env_changes(item_name):
    if request.method == "GET":
        return render_template(
            "add_item/env_changes.html",
            item_name=item_name,
            is_toggle_selected=session.get(r.USE_GROUP_VALUES_SK, False),
            group_info=env_changes_json_to_html_ids(
                get_group_env_changes_info(session.get(r.GROUP_NAME_SK, ""), item_name),
                get_current_category_info(item_name, r.ENV_CHANGES_CAT_KEY)),
            # TODO - temporarily on.
            show_group=True
        )

    if maybe_group_toggle_update_saved(session, request.form):
        return redirect(url_for("add.env_changes", item_name=item_name))

    # TODO - handle lists in getting JSON data to website. (in all categories).

    # Save data
    data = {r.EC_CHANGE_J_KEY: request.form["change_text"]}
    write_json_category_to_file(item_name, r.ENV_CHANGES_CAT_KEY, data)
    # TODO: don't write to group it's already in there!!
    maybe_write_category_to_group(session[r.GROUP_NAME_SK], item_name, r.ENV_CHANGES_CAT_KEY, data)

    return either_move_next_category_or_repeat(item_name, "add.env_changes", request.form)

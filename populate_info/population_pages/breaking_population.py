import typing

from flask import redirect, render_template, request, session, url_for

import populate_info.resources as r
from populate_info.group_utils import (
    get_group_breaking_info, maybe_group_toggle_update_saved, maybe_write_category_to_group, get_next_group_data,
    get_button_choice, should_show_group)
from populate_info.json_utils import write_json_category_to_file, get_current_category_info
from populate_info.navigation_utils import either_move_next_category_or_repeat
from populate_info.population_pages import item_blueprint

REQ_TOOL_HTML_TO_JSON = {
    "tool-no": "none",
    "tool-any": "any",
    "tool-spec": "specific"
}
REQ_TOOL_JSON_TO_HTML = {
    value: f"requires-{key}" for key, value in REQ_TOOL_HTML_TO_JSON.items()}

SILK_TOUCH_HTML_TO_JSON = {
    "silk-yes-v": True,
    "silk-no-v": False
}
SILK_TOUCH_JSON_TO_HTML = {True: f"requires-silk-yes", False: f"requires-silk-no"}


def breaking_json_to_html_ids(group_data: typing.Union[dict, list], item_data) -> dict[str, list[str]]:
    """
    Takes an object taken from JSON that contains the breaking data and returns the corresponding information that
    should be passed to the webpage.

    :param group_data: breaking data from the existing group
    :param item_data: breaking data for the current item.
     """

    # TODO - handle case where the number in the old group and this group no longer match up correctly.
    if len(group_data) == 0:
        return {}

    data_to_populate = get_next_group_data(group_data, item_data)
    result = {
        # always has requires tool and silk.
        "to-mark-checked": [
            REQ_TOOL_JSON_TO_HTML[data_to_populate[r.BREAKING_REQ_TOOL_KEY]],
            SILK_TOUCH_JSON_TO_HTML[data_to_populate[r.BREAKING_SILK_TOUCH_KEY]]
        ],
        "reveal": [],  # TODO - test this!!
        "button-choice": get_button_choice(group_data, item_data),
        "dropdown-select": {}
    }
    # Add the special cases
    if data_to_populate[r.BREAKING_REQ_TOOL_KEY] == "specific":
        result["dropdown-select"]["specific-tool-select"] = r.idify_tool_name(
            data_to_populate[r.BREAKING_REQ_SPECIFIC_TOOL_KEY])
        result["reveal"].append("spec-tool-select")
    # TODO - make sure to add a possible no key for the fastest silk.
    if r.BREAKING_FASTEST_TOOL_KEY in data_to_populate:
        result["to-mark-checked"].append("fastest-tool-yes")
        result["dropdown-select"]["fastest-specific-tool-select"] = r.idify_tool_name(
            data_to_populate[r.BREAKING_FASTEST_TOOL_KEY])
        result["reveal"].append("fastest-specific-tool-select")
    else:
        result["to-mark-checked"].append("fastest-tool-no")

    return result


@item_blueprint.route("/breaking/<item_name>", methods=["GET", "POST"])
def breaking(item_name):
    """ Handles populating the breaking obtainment method."""
    # TODO - update all uses of session[r.GROUP_NAME] to session.get with a default group name.
    group_name = session.get(r.GROUP_NAME_SK, "")
    if request.method == "GET":
        return render_template(
            "add_item/breaking.html",
            item_name=item_name,
            group_name=group_name,
            is_toggle_selected=session.get(r.USE_GROUP_VALUES_SK, False),
            group_info=breaking_json_to_html_ids(
                get_group_breaking_info(group_name, item_name),
                get_current_category_info(item_name, r.BREAKING_CAT_KEY)),
            # TODO - toggle for testing.
            # show_group=True)
            show_group=should_show_group(group_name))

    if maybe_group_toggle_update_saved(session, request.form):
        return redirect(url_for("add.breaking", item_name=item_name))

    # Get the data.
    data = {
        r.BREAKING_REQ_TOOL_KEY: REQ_TOOL_HTML_TO_JSON[request.form["requires-tool"]],
        r.BREAKING_SILK_TOUCH_KEY: SILK_TOUCH_HTML_TO_JSON[request.form["requires-silk"]]
    }

    # Add the specific tool name if it is required.
    if data[r.BREAKING_REQ_TOOL_KEY] == "specific":
        data[r.BREAKING_REQ_SPECIFIC_TOOL_KEY] = r.clean_up_tool_name(request.form["specific-tool"])

    if request.form["fastest-tool"] == "fastest-yes":
        data[r.BREAKING_FASTEST_TOOL_KEY] = r.clean_up_tool_name(request.form["fastest-specific-tool"])

    write_json_category_to_file(item_name, r.BREAKING_CAT_KEY, data)
    maybe_write_category_to_group(session[r.GROUP_NAME_SK], item_name, r.BREAKING_CAT_KEY, data)

    return either_move_next_category_or_repeat(item_name, "add.breaking", request.form)

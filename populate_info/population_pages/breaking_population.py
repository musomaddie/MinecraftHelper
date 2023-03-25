from flask import redirect, render_template, request, session, url_for

import populate_info.resources as r
from populate_info.group_utils import maybe_group_toggle_update_saved
from populate_info.navigation_utils import either_move_next_category_or_repeat
from populate_info.population_pages import item_blueprint

REQ_TOOL_HTML_TO_JSON = {
    "tool_no": "none",
    "tool_any": "any",
    "tool_spec": "specific"
}
REQ_TOOL_JSON_TO_HTML = {value: key for key, value in REQ_TOOL_HTML_TO_JSON.items()}

SILK_TOUCH_HTML_TO_JSON = {
    "silk_yes": True,
    "silk_no": False
}
SILK_TOUCH_JSON_TO_HTML = {value: key for key, value in SILK_TOUCH_HTML_TO_JSON.items()}


@item_blueprint.route("/breaking/<item_name>", methods=["GET", "POST"])
def breaking(item_name):
    """ Handles populating the breaking obtainment method."""
    if request.method == "GET":
        return render_template(
            "add_item/breaking.html",
            item_name=item_name,
            group_name=session[r.GROUP_NAME_SK],
            is_toggle_selected=session.get(r.USE_GROUP_VALUES_SK, False),
            # TODO - temporarily on for testing!
            show_group=True)

    if maybe_group_toggle_update_saved(session, request.form):
        return redirect(url_for("add.breaking", item_name=item_name))

    # Get the data.
    # TODO: how do handle group with multiple?? -> what button should be pressed?? -> return to this later - do normal
    #  thing first.
    data = {
        r.BREAKING_REQ_TOOL_KEY: REQ_TOOL_HTML_TO_JSON[request.form["requires_tool"]],
        r.BREAKING_SILK_TOUCH_KEY: SILK_TOUCH_HTML_TO_JSON[request.form["requires_silk"]]
    }

    # Add the specific tool name if it is required.
    if data[r.BREAKING_REQ_TOOL_KEY] == "specific":
        data[r.BREAKING_REQ_SPECIFIC_TOOL_KEY] = r.clean_up_tool_name(request.form["specific_tool"])

    if "fastest_tool" in request.form:
        data[r.BREAKING_FASTEST_TOOL_KEY] = r.clean_up_tool_name(request.form["fastest_specific_tool"])

    return either_move_next_category_or_repeat(
        item_name, "add.breaking", session[r.METHOD_LIST_SK], request.form)

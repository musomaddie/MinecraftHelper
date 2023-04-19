$(document).ready(function () {
    // Start with the fastest tool default set to no so that updates from group will change it.
    document.getElementById("fastest-tool-no").checked = true
    const select_fastest = document.getElementById("fastest_specific_tool_select");

    document.getElementById("requires-tool-no")
        .addEventListener(
            'change',
            (event) =>
                add_to_class_list_listener(event, select_fastest, "hidden"));
    document.getElementById("fastest-tool-yes")
        .addEventListener(
            'change',
            (event) =>
                remove_from_class_list_listener(event, select_fastest, "hidden"));

    // Set up class listener for buttons to hide things
    const select_required = document.getElementById("spec_tool_select");

    document.getElementById("requires-tool-no")
        .addEventListener(
            'change',
            (event) =>
                add_to_class_list_listener(event, select_required, "hidden"));
    document.getElementById("requires-tool-yes")
        .addEventListener(
            'change',
            (event) =>
                add_to_class_list_listener(event, select_required, "hidden"));
    document.getElementById("requires-tool-specific")
        .addEventListener(
            'change',
            (event) =>
                remove_from_class_list_listener(event, select_required, "hidden"));
});

function add_to_class_list_listener(event, modify_element, class_name) {
    if (event.currentTarget.checked
        && !modify_element.classList.contains(class_name)) {
        modify_element.classList.add(class_name);
    }
}

function remove_from_class_list_listener(event, modify_element, class_name) {
    if (event.currentTarget.checked) {
        modify_element.classList.remove(class_name)
    }

}


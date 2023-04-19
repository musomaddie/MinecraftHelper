$(document).ready(function () {
    // Start by setting default values for the dropdown, so they can later be overridden by group selections!
    document.getElementById("requires-tool-no").checked = true
    document.getElementById("fastest-tool-no").checked = true
    document.getElementById("silk-no").checked = true

    // Set up listeners to reveal hidden menus when appropriate.
    const select_fastest = document.getElementById("fastest-specific-tool-select");
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

    const select_required = document.getElementById("spec-tool-select");
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


$(document).ready(function () {
    setup_object_listeners();
    // If we shouldn't use the group values, still include some default ones.
    if (!(breaking_config_vars["show-group"] && breaking_config_vars["is-toggle-selected"])) {
        document.getElementById("requires-tool-no").checked = true
        document.getElementById("fastest-tool-no").checked = true
        document.getElementById("requires-silk-no").checked = true
        return
    }
    breaking_config_vars["group-info"]["reveal"].forEach(
        element => document.getElementById(element).classList.remove("hidden"));
    breaking_config_vars["group-info"]["to-mark-checked"].forEach(
        element => {
            console.log(element);
            document.getElementById(element).checked = true
        }
    );
    for (let key in breaking_config_vars["group-info"]["dropdown-select"]) {
        document.getElementById(key).value = breaking_config_vars["group-info"]["dropdown-select"][key];
    }
});

function setup_object_listeners() {
    // Start by setting default values for the dropdown, so they can later be overridden by group selections!
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
    document.getElementById("requires-tool-any")
        .addEventListener(
            'change',
            (event) =>
                add_to_class_list_listener(event, select_required, "hidden"));
    document.getElementById("requires-tool-specific")
        .addEventListener(
            'change',
            (event) =>
                remove_from_class_list_listener(event, select_required, "hidden"));

}

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


$(document).ready(function () {
    // Include default values if we shouldn't use group values.
    if (!(crafting_config_vars["show-group"] && crafting_config_vars["is-toggle-selected"])) {
        document.getElementById("flexible-positioning-no").checked = true
        document.getElementById("small-grid-no").checked = true
    }

    Object.entries(crafting_config_vars["group-info"]["to-fill"]).forEach(
        (entry) => {
            // entry 0 -> id entry 1 -> value
            document.getElementById(entry[0]).value = entry[1];
        });

    crafting_config_vars["group-info"]["to-mark-checked"].forEach(
        element => {
            document.getElementById(element).checked = true
        }
    );


});

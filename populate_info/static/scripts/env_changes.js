$(document).ready(function () {
    if (!(config_vars["show-group"] && config_vars["is-toggle-selected"])) {
        return;
    }

    console.log(env_changes_vars["group-info"]["button-choice"]);

    document.getElementById("change-text").value = env_changes_vars["group-info"]["change-text"]
    document.getElementById(env_changes_vars["group-info"]["button-choice"]).classList.add("should-select");
});

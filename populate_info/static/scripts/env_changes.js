$(document).ready(function () {
    if (!(config_vars["show-group"] && config_vars["is-toggle-selected"])) {
        return;
    }
    document.getElementById("change-text").value = env_changes_vars["group-info"]["change-text"]
    document.getElementById(env_changes_vars["group-info"]["button-choice"]).classList.add("should-select");
});

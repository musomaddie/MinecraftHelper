$(document).ready(function () {
    // Needed for nice switch layout.
    const checkbox = document.getElementById("switch-checkbox");
    const track = document.getElementById("track")
    checkbox.addEventListener('change', (event) => {
        if (event.currentTarget.checked) {
            track.classList.add("on-track")
        } else {
            track.classList.remove("on-track");
        }
    });

    if (!config_vars["show-group"]) {
        return;
    }
    if (config_vars["is-toggle-selected"]) {
        document.getElementById("switch-checkbox").checked = true;
        track.classList.add("on-track")
    }
});

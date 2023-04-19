$(document).ready(function () {
    // Set up class listener for buttons to hide things
    const select_menu = document.getElementById("spec_tool_select");

    document.getElementById("requires-tool-no")
        .addEventListener(
            'change', (event) => {
                if (event.currentTarget.checked) {
                    select_menu.classList.add("hidden");
                }
            });
    document.getElementById("requires-tool-yes").addEventListener(
        'change', (event) => {
            if (event.currentTarget.checked && !select_menu.classList.contains("hidden")) {
                select_menu.classList.add("hidden");
            }
        });
    document.getElementById("requires-tool-specific").addEventListener(
        'change', (event) => {
            if (event.currentTarget.checked) {
                select_menu.classList.remove("hidden");
            }
        });
})


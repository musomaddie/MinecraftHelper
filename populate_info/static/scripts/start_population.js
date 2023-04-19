$(document).ready(function () {
    // Set up listeners for the values.
    const ids_to_spans = {
        "breaking-cbox": "breaking-span",
        "crafting-cbox": "crafting-span",
        "env-changes-cbox": "env-changes-span"
    }
    Object.entries(ids_to_spans).forEach(
        function (key) {
            document.getElementById(key[0]).addEventListener(
                'change', (event) => {
                    let span = document.getElementById(key[1]);
                    let tickedSpan = document.createElement("span");
                    tickedSpan.classList.add("material-symbols-outlined")
                    tickedSpan.innerText = "done"
                    if (event.currentTarget.checked) {
                        span.append(tickedSpan);
                    } else {
                        span.innerHTML = "";
                    }
                }
            )
        });

    // Quit if we shouldn't be updating these values.
    if (!start_config["show-group"]) {
        return
    }
    start_config["group-categories"].forEach(
        element => {
            document.getElementById(element).checked = true
            let span = document.getElementById(ids_to_spans[element]);
            let tickedSpan = document.createElement("span");
            tickedSpan.classList.add("material-symbols-outlined")
            tickedSpan.innerText = "done"
            span.append(tickedSpan);
        }
    );
});

function blockStartFormLoaded() {
    console.log("LOADED!")
}

const block_start_form = document.getElementById("block_start_form")
const URL_STRING = "127.0.0.1:5000"

// block_start_form.addEventListener("load", blockStartFormLoaded)

// TODO: this is run but the page reloads and the changes are lost!
function loadExistingValues() {
    console.log("Running");
    // if (document.URL.includes("add_item")) {
    //     console.log("add item homepage")
    //     const items_url = 'http://127.0.0.1:5000/preexisting_group/obtaining'
    //     fetch(items_url)
    //         .then(response => response.json())
    //         .then(data => {
    //             data.forEach(checkbox_id => {
    //                 document.getElementById(checkbox_id).checked = true;
    //             })
    //         })
    // }
}

// $(document).ready(function () {
//     // document
//     if (document.URL.includes("add_item")) {
//         console.log("add item homepage")
//
//         const items_url = 'http://127.0.0.1:5000/preexisting_group/obtaining'
//         fetch(items_url)
//             .then(response => response.json())
//             .then(data => {
//                 data.forEach(checkbox_id => {
//                     document.getElementById(checkbox_id).checked = true;
//                 })
//             })
//     }
// })

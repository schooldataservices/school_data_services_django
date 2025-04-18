document.addEventListener("DOMContentLoaded", function () {
    // Attach event listeners to pagination links
    document.querySelectorAll(".page-link").forEach(function (link) {
        link.addEventListener("click", function (event) {
            event.preventDefault();
            const page = this.getAttribute("data-page");
            fetchPage(page);
        });
    });

    // Attach event listeners to filter dropdowns
    const filters = ["priorityFilter", "dateFilter", "completionFilter", "userFilter"];
    filters.forEach(function (filterId) {
        const filterElement = document.getElementById(filterId);
        if (filterElement) {
            filterElement.addEventListener("change", function () {
                fetchPage(1); // Reset to page 1 when a filter changes
            });
        }
    });
});

function fetchPage(page) {
    console.log("Fetching page:", page);
    const url = new URL(window.location.href);
    url.searchParams.set("page", page);
    url.searchParams.set("priority", document.getElementById("priorityFilter").value);
    url.searchParams.set("date", document.getElementById("dateFilter").value);
    url.searchParams.set("completion", document.getElementById("completionFilter").value);
    url.searchParams.set("user", document.getElementById("userFilter") ? document.getElementById("userFilter").value : "all");

    fetch(url, {
        headers: {
            "X-Requested-With": "XMLHttpRequest"
        }
    })
        .then(response => response.json())
        .then(data => {
            const requestListContainer = document.getElementById("requestListContainer");
            const paginationInfo = document.getElementById("pagination-info");

            // Check if there are no requests
            if (data.total_results === 0) {
                requestListContainer.innerHTML = `
                <table>
                    <thead>
                        <tr>
                            <th></th>
                            <th>ID</th>
                            <th>Date Submitted</th>
                            <th>Priority</th>
                            <th>Desired Completion Date</th>
                            <th>User</th>
                            <th>Email Content</th>
                            <th>Completion Status</th>
                        </tr>
                    </thead>
                    <tbody>
                        <tr>
                            <td colspan="7" style="text-align:center;">No historical requests found</td>
                        </tr>
                    </tbody>
                </table>
            `;
                paginationInfo.innerHTML = ""; // Clear pagination info if no results
            } else {
                // Populate the table with the returned HTML
                const requestListContainer = document.getElementById("requestListContainer");

                if (!requestListContainer) {
                    console.warn("Warning: Element with ID 'requestListContainer' not found. Skipping table update.");
                    return; // Exit the function if the element is not found
                }

                requestListContainer.innerHTML = data.html; // Populate the table
                paginationInfo.innerHTML = `Page ${data.current_page} of ${data.total_pages} (Total results: ${data.total_results})`;

                // Reattach event listeners for pagination links
                document.querySelectorAll(".page-link").forEach(function (link) {
                    link.addEventListener("click", function (event) {
                        event.preventDefault();
                        const page = this.getAttribute("data-page");
                        fetchPage(page);
                    });
                });

                // Reattach event listeners from request_page.js
                if (typeof attachEventListeners === "function") { 
                    console.log("attachEventListeners is being called");
                    attachEventListeners();
                } else {
                    console.error("attachEventListeners is not defined or accessible");
                }
            }
        })
        .catch(error => console.error("Error:", error));
}



// All of the listeners from request_page.js here function attachEventListeners() { need to be re-attached


// Pagination can not
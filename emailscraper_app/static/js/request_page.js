document.getElementById("toggleTableButton").addEventListener("click", function() {
    let tableContainer = document.getElementById("historicalRequestsContainer");
    
    if (tableContainer.style.display === "none") {
        tableContainer.style.display = "block";
        this.textContent = "Hide Historical Requests"; // Change button text
    } else {
        tableContainer.style.display = "none";
        this.textContent = "Show Historical Requests"; // Change button text
    }
});

// Priority Filter Logic
document.getElementById("priorityFilter").addEventListener("change", function() {
    applyFilters();
});

// Date Filter Logic
document.getElementById("dateFilter").addEventListener("change", function() {
    applyFilters();
});

function applyFilters() {
    let selectedPriority = document.getElementById("priorityFilter").value.toLowerCase();
    let selectedDate = document.getElementById("dateFilter").value.toLowerCase();
    let rows = document.querySelectorAll("table tbody tr");

    rows.forEach(row => {
        let priority = row.children[1].textContent.toLowerCase();  // Priority in second column
        let dateSubmitted = new Date(row.children[0].textContent); // Date in first column (assumed format 'Feb. 5, 2025, 7:50 p.m.')
        let scheduleTime = new Date(row.children[2].textContent); // Schedule Time in third column (assumed format '2025-01-31 12:00:00')

        // Apply Date Filtering Logic
        let dateMatch = true;
        if (selectedDate === "today") {
            let today = new Date();
            today.setHours(0, 0, 0, 0);
            dateMatch = scheduleTime.toDateString() === today.toDateString();
        } else if (selectedDate === "last7days") {
            let last7Days = new Date();
            last7Days.setDate(last7Days.getDate() - 7);
            dateMatch = scheduleTime >= last7Days;
        } else if (selectedDate === "thismonth") {
            let firstDayOfMonth = new Date(new Date().getFullYear(), new Date().getMonth(), 1);
            dateMatch = scheduleTime >= firstDayOfMonth;
        }

        // Apply the filters for both priority and date
        if ((selectedPriority === "all" || priority === selectedPriority) && dateMatch) {
            row.style.display = "";  // Show the row
        } else {
            row.style.display = "none";  // Hide the row
        }
    });
}


// Initialize Flatpickr for Date and Time input
flatpickr(".datetimepicker", {
    enableTime: true,   
    dateFormat: "Y-m-d H:i",  
    minDate: "today",   
    time_24hr: true     
});

document.addEventListener("DOMContentLoaded", function() {
    const statusCheckboxes = document.querySelectorAll('.completion-status-toggle'); // All completion status checkboxes

    statusCheckboxes.forEach(checkbox => {
        checkbox.addEventListener('change', function() {
            const requestId = checkbox.getAttribute('data-id');  // Get the config ID from the checkbox's data-id attribute
            const isChecked = checkbox.checked;  // Get the checkbox state (checked or unchecked)

            // Send the AJAX request to update the completion status
            fetch(`/update-completion-status/${requestId}/`, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                    'X-CSRFToken': getCSRFToken()  // CSRF token for security
                },
                body: JSON.stringify({
                    'completion_status': isChecked,
                    'config_id': requestId  // Include the ID of the config you're updating
                })
            })
            .then(response => response.json())
            .then(data => {
                if (data.success) {
                    // Update the status text or style to reflect the change
                    const statusCell = document.querySelector(`#status-cell-${requestId}`);
                    if (statusCell) {
                        statusCell.innerHTML = isChecked ? "Completed" : "Pending";  // Example of updating text
                    }
                    console.log('Status updated successfully');
                } else {
                    console.error('Error updating status');
                    // Optionally handle the error case (e.g., display an alert)
                }
            })
            .catch(error => console.error('Error:', error));
        });
    });

    // Helper function to get the CSRF token
    function getCSRFToken() {
        const csrfToken = document.cookie.match(/csrftoken=([^;]+)/);
        return csrfToken ? csrfToken[1] : '';
    }
});


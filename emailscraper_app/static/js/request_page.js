import { fetchNotificationCount } from './profile_dropdown_functionality.js';

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
    console.log("Priority filter changed to:", this.value);
    fetchFilteredRequests();
});

// Date Filter Logic
document.getElementById("dateFilter").addEventListener("change", function() {
    console.log("Date filter changed to:", this.value);
    fetchFilteredRequests();
});

// Completion Filter Logic
document.getElementById("completionFilter").addEventListener("change", function() {
    console.log("Completion filter changed to:", this.value);
    fetchFilteredRequests();
});

// User Filter Logic (for superusers)
const userFilter = document.getElementById("userFilter");
if (userFilter) {
    userFilter.addEventListener("change", function() {
        console.log("User filter changed to:", this.value);
        fetchFilteredRequests();
    });
}

function fetchFilteredRequests() {
    let selectedUser;
    if (userFilter) {
        selectedUser = userFilter.value.toLowerCase();
    } else {
        selectedUser = document.getElementById("loggedInUser").value.toLowerCase();
    }
    let selectedPriority = document.getElementById("priorityFilter").value.toLowerCase();
    let selectedDate = document.getElementById("dateFilter").value.toLowerCase();
    let selectedCompletion = document.getElementById("completionFilter").value.toLowerCase();

    console.log("Fetching filtered requests:", { selectedUser, selectedPriority, selectedDate, selectedCompletion });
    console.log("Fetching from:", `/filter-requests/?user=${selectedUser}&priority=${selectedPriority}&date=${selectedDate}&completion=${selectedCompletion}`);

    fetch(`/filter-requests/?user=${selectedUser}&priority=${selectedPriority}&date=${selectedDate}&completion=${selectedCompletion}`)
        .then(response => response.json())
        .then(data => {
            updateTable(data.requests);
        })
        .catch(error => console.error('Error:', error));
}

function updateTable(requests) {
    const tbody = document.querySelector("table tbody");
    tbody.innerHTML = ''; // Clear existing rows

    if (requests.length === 0) {
        console.log('No historical requests found');
        tbody.innerHTML = '<tr><td colspan="7" style="text-align:center;">No historical requests found</td></tr>';
        return;
    }

    requests.forEach(req => {
        const row = document.createElement('tr');

        row.innerHTML = `
            <td>
                <button class="delete-request" data-id="${req.id}">
                    <i class="fas fa-trash-alt"></i>
                </button>
            </td>
            <td>${req.date_submitted}</td>
            <td>${req.priority_status}</td>
            <td>${req.schedule_time}</td>
            <td>${req.creator}</td>
            <td contenteditable="true" class="editable-email-content" data-id="${req.id}">
                ${req.email_content}
            </td>
            <td id="status-cell-${req.id}">
                ${req.completion_status}
                <input type="checkbox" class="completion-status-toggle" data-id="${req.id}" ${req.completion_status === 'Completed' ? 'checked' : ''}>
            </td>
        `;

        tbody.appendChild(row);
    });

    // Re-attach event listeners for the new rows
    attachEventListeners();
}

// Initialize Flatpickr for Date and Time input
flatpickr(".datetimepicker", {
    enableTime: true,   
    dateFormat: "Y-m-d H:i",  
    minDate: "today",   
    time_24hr: true     
});

document.addEventListener("DOMContentLoaded", function () {
    attachEventListeners();
    if (userFilter) { // Only fetch filtered requests if userFilter exists (i.e., user is a superuser)
        fetchFilteredRequests(); // Fetch filtered requests on page load
    }
    fetchNotificationCount(); // Fetch and update the notification badge on page load

    const checkboxes = document.querySelectorAll('.completion-status-toggle');
    console.log(`Found ${checkboxes.length} checkboxes`);
});

function attachEventListeners() {
    // Handle editable email cells
    const editableEmailCells = document.querySelectorAll('.editable-email-content');

    editableEmailCells.forEach(cell => {
        // Add blur event listener to handle saving content
        cell.addEventListener('blur', function () {
            const requestId = cell.getAttribute('data-id');
            const updatedContent = cell.textContent.trim();

            // Validate the request ID and updated content
            if (!requestId || !updatedContent) {
                return; // Exit if request ID or content is invalid
            }

            console.log(`Updating email content for request ID: ${requestId}`);

            // Send the updated content to the backend
            fetch(`/update-email-content/${requestId}/`, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                    'X-CSRFToken': getCSRFToken()
                },
                body: JSON.stringify({
                    'email_content': updatedContent
                })
            })
            .then(response => response.json())
            .then(data => {
                if (data.success) {
                    fetchNotificationCount(); // Update the notification badge
                    console.log('Email content updated successfully');
                } else {
                    console.error('Error updating email content:', data.error);
                }
            })
            .catch(error => console.error('Error:', error));
        });
    });

    // Handle completion status checkboxes
    const statusCheckboxes = document.querySelectorAll('.completion-status-toggle');

    statusCheckboxes.forEach(checkbox => {
        checkbox.addEventListener('change', function () {
            const requestId = checkbox.getAttribute('data-id');
            const isChecked = checkbox.checked;

            console.log(`Updating completion status for request ID: ${requestId}, Checked: ${isChecked}`);

            // Send the updated status to the backend
            fetch(`/update-completion-status/${requestId}/`, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                    'X-CSRFToken': getCSRFToken()
                },
                body: JSON.stringify({
                    'completion_status': isChecked,
                    'config_id': requestId
                })
            })
            .then(response => response.json())
            .then(data => {
                if (data.success) {
                    fetchFilteredRequests(); // Fetch filtered requests after updating completion status
                    fetchNotificationCount(); // Update the notification badge
                    console.log('Status updated successfully');
                } else {
                    console.error('Error updating status');
                }
            })
            .catch(error => console.error('Error:', error));
        });
    });

    const deleteButtons = document.querySelectorAll('.delete-request');

    deleteButtons.forEach(button => {
        button.addEventListener('click', function () {
            const requestId = button.getAttribute('data-id');

            console.log(`Deleting request with ID: ${requestId}`);

            // Confirm deletion
            if (!confirm('Are you sure you want to delete this request?')) {
                return;
            }

            // Send DELETE request to the backend
            fetch(`/delete-request/${requestId}/`, {
                method: 'DELETE',
                headers: {
                    'X-CSRFToken': getCSRFToken()
                }
            })
            .then(response => response.json())
            .then(data => {
                if (data.success) {
                    console.log('Request deleted successfully');
                    // Remove the row from the table
                    const row = button.closest('tr');
                    if (row) {
                        row.remove();
                    }
                    fetchNotificationCount(); // Update the notification badge
                    console.log('Request deleted successfully');
                } else {
                    console.error('Error deleting request:', data.error);
                }
            })
            .catch(error => console.error('Error:', error));
        });
    });

}

function getCSRFToken() {
    const csrfToken = document.cookie.match(/csrftoken=([^;]+)/);
    return csrfToken ? csrfToken[1] : '';
}

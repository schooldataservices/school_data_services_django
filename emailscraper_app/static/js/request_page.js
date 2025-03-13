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
    let selectedUser = userFilter ? userFilter.value.toLowerCase() : "all";
    let selectedPriority = document.getElementById("priorityFilter").value.toLowerCase();
    let selectedDate = document.getElementById("dateFilter").value.toLowerCase();
    let selectedCompletion = document.getElementById("completionFilter").value.toLowerCase();

    console.log("Fetching filtered requests:", { selectedUser, selectedPriority, selectedDate, selectedCompletion });

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

document.addEventListener("DOMContentLoaded", function() {
    attachEventListeners();
    if (userFilter) { // Only fetch filtered requests if userFilter exists (i.e., user is a superuser)
        fetchFilteredRequests(); // Fetch filtered requests on page load
    }
});

function attachEventListeners() {
    const statusCheckboxes = document.querySelectorAll('.completion-status-toggle');

    statusCheckboxes.forEach(checkbox => {
        checkbox.addEventListener('change', function() {
            const requestId = checkbox.getAttribute('data-id');
            const isChecked = checkbox.checked;

            console.log(`Updating completion status for request ID: ${requestId}, Checked: ${isChecked}`);

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
                    const statusCell = document.querySelector(`#status-cell-${requestId}`);
                    if (statusCell) {
                        statusCell.innerHTML = isChecked ? "Completed" : "Pending";
                    }
                    console.log('Status updated successfully');
                } else {
                    console.error('Error updating status');
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

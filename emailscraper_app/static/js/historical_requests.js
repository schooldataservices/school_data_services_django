function attachEventListeners() {

    const statusCheckboxes = document.querySelectorAll('.completion-status-toggle');

    statusCheckboxes.forEach(checkbox => {
        checkbox.addEventListener('change', function () {
            const requestId = checkbox.getAttribute('data-id');
            const isChecked = checkbox.checked;

            // Update the text dynamically
            const statusTextElement = document.querySelector(`#status-cell-${requestId} .status-text`);
            if (statusTextElement) {
                statusTextElement.textContent = isChecked ? 'Completed' : 'Pending';
            }

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
                    fetchNotifications(); // Update the notification badge
                    // console.log('Status updated successfully');
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
                    // Fetch the next available request ID
                    fetch(`/get-next-request-id/?id=${requestId}`, { // Pass the current ID in the query string
                        method: 'GET',
                        headers: {
                            'Content-Type': 'application/json'
                        }
                    })
                    .then(response => response.json())
                    .then(nextData => {
                        if (nextData.next_request_id) {
                            const successMessage = `Request ID ${requestId} deleted successfully.`;
                            const nextUrl = `/historical-requests/?id=${nextData.next_request_id}&message=${encodeURIComponent(successMessage)}`;
                            window.location.href = nextUrl;
                        } else {
                            // No more requests available
                            alert('No more requests available.');
                            const successMessage = `Request ID ${requestId} deleted successfully.`;
                            const defaultUrl = `/historical-requests/?message=${encodeURIComponent(successMessage)}`;
                            window.location.href = defaultUrl;
                        }
                    })
                    .catch(error => console.error('Error fetching next request ID:', error));
                } else {
                    console.error('Error deleting request:', data.error);
                }
            })
            .catch(error => console.error('Error:', error));
        });
    });

    const containers = document.querySelectorAll(".editable-email-container");

    containers.forEach(container => {
        const contentDiv = container.querySelector(".editable-email-content");
        const editButton = container.querySelector(".edit-button");
        const saveButton = container.querySelector(".save-button");

        // Enable editing when the Edit button is clicked
        editButton.addEventListener("click", function () {
            contentDiv.contentEditable = "true"; // Enable editing
            contentDiv.focus(); // Focus on the content
            editButton.style.display = "none"; // Hide the Edit button
            saveButton.style.display = "inline-block"; // Show the Save button
        });

        // Save changes when the Save button is clicked
        saveButton.addEventListener("click", function () {
            const requestId = contentDiv.getAttribute("data-id");
            const updatedContent = contentDiv.innerHTML.trim(); // Get the updated content

            // Disable editing
            contentDiv.contentEditable = "false";
            editButton.style.display = "inline-block"; // Show the Edit button
            saveButton.style.display = "none"; // Hide the Save button

            // Send the updated content to the backend
            fetch(`/update-email-content/${requestId}/`, {
                method: "POST",
                headers: {
                    "Content-Type": "application/json",
                    "X-CSRFToken": getCSRFToken()
                },
                body: JSON.stringify({
                    email_content: updatedContent
                })
            })
            .then(response => response.json())
            .then(data => {
                if (data.success) {
                    fetchNotifications();
                } else {
                    console.error("Error updating email content:", data.error);
                }
            })
            .catch(error => console.error("Error:", error));
        });
    });

    // Function to get CSRF token
    function getCSRFToken() {
      const cookie = document.cookie.match(/csrftoken=([^;]+)/);
      if (cookie) return cookie[1];
      const meta = document.querySelector('meta[name="csrf-token"]');
      return meta ? meta.content : '';
    }
}

document.addEventListener('DOMContentLoaded', () => {
    attachEventListeners();
});
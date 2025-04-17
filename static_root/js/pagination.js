document.addEventListener('DOMContentLoaded', function() {
    document.querySelectorAll('.page-link').forEach(function(link) {
        link.addEventListener('click', function(event) {
            event.preventDefault();
            const page = this.getAttribute('data-page');
            fetchPage(page);
        });
    });

    document.getElementById('priorityFilter').addEventListener('change', function() {
        fetchPage(1);
    });

    document.getElementById('dateFilter').addEventListener('change', function() {
        fetchPage(1);
    });

    document.getElementById('completionFilter').addEventListener('change', function() {
        fetchPage(1);
    });

    attachCheckboxListeners();
    attachEditableContentListeners();
    attachDeleteButtonListeners();
});

function fetchPage(page) {
    const url = new URL(window.location.href);
    url.searchParams.set('page', page);
    url.searchParams.set('priority', document.getElementById('priorityFilter').value);
    url.searchParams.set('date', document.getElementById('dateFilter').value);
    url.searchParams.set('completion', document.getElementById('completionFilter').value);

    fetch(url, {
        headers: {
            'X-Requested-With': 'XMLHttpRequest'
        }
    })
    .then(response => response.json())
    .then(data => {
        document.getElementById('requestListContainer').innerHTML = data.html;
        document.getElementById('pagination-info').innerHTML = `Page ${data.current_page} of ${data.total_pages} (Total results: ${data.total_results})`;
        document.querySelectorAll('.page-link').forEach(function(link) {
            link.addEventListener('click', function(event) {
                event.preventDefault();
                const page = this.getAttribute('data-page');
                fetchPage(page);
            });
        });
        attachCheckboxListeners();
        attachEditableContentListeners();
        attachDeleteButtonListeners();
    });
}

function attachCheckboxListeners() {
    const statusCheckboxes = document.querySelectorAll('.completion-status-toggle');

    statusCheckboxes.forEach(checkbox => {
        checkbox.addEventListener('change', function() {
            const requestId = checkbox.getAttribute('data-id');
            const isChecked = checkbox.checked;

            // console.log(`Updating completion status for request ID: ${requestId}, Checked: ${isChecked}`);

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
                    // console.log('Status updated successfully');
                } else {
                    console.error('Error updating status');
                }
            })
            .catch(error => console.error('Error:', error));
        });
    });
}

function attachEditableContentListeners() {
    const editableEmailContents = document.querySelectorAll('.editable-email-content');

    editableEmailContents.forEach(cell => {
        let timeoutId;
        cell.addEventListener('input', function() {
            clearTimeout(timeoutId);
            timeoutId = setTimeout(() => {
                const requestId = cell.getAttribute('data-id');
                const newContent = cell.innerHTML;

                // console.log(`Auto-saving email content for request ID: ${requestId}, New Content: ${newContent}`);

                fetch(`/update-email-content/${requestId}/`, {
                    method: 'POST',
                    headers: {
                        'Content-Type': 'application/json',
                        'X-CSRFToken': getCSRFToken()
                    },
                    body: JSON.stringify({
                        'email_content': newContent
                    })
                })
                .then(response => response.json())
                .then(data => {
                    if (data.success) {
                        // console.log('Email content auto-saved successfully');
                    } else {
                        console.error('Error auto-saving email content');
                    }
                })
                .catch(error => console.error('Error:', error));
            }, 1000); // Adjust the delay as needed
        });
    });
}

function attachDeleteButtonListeners() {
    const deleteButtons = document.querySelectorAll('.delete-request');

    deleteButtons.forEach(button => {
        button.addEventListener('click', function() {
            const requestId = button.getAttribute('data-id');

            // console.log(`Deleting request ID: ${requestId}`);

            fetch(`/delete-request/${requestId}/`, {
                method: 'DELETE',
                headers: {
                    'Content-Type': 'application/json',
                    'X-CSRFToken': getCSRFToken()
                }
            })
            .then(response => response.json())
            .then(data => {
                if (data.success) {
                    // console.log('Request deleted successfully');
                    fetchPage(1); // Refresh the page to reflect the deletion
                } else {
                    console.error('Error deleting request');
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
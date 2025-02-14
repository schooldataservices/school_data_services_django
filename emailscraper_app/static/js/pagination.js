// filepath: /c:/Users/becky/Desktop/Git_Directory/Django_Email_Hub/emailscraper_app/static/js/pagination.js
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
    });
}

function attachCheckboxListeners() {
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
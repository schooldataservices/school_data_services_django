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

function getCSRFToken() {
    const csrfToken = document.cookie.match(/csrftoken=([^;]+)/);
    return csrfToken ? csrfToken[1] : '';
}
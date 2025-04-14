$(document).ready(function() {
    console.log("Document is ready");
    $('.dropdown-toggle').dropdown();
    console.log("Dropdown initialized");

    $('#profileDropdown').on('click', function() {
        console.log("Profile image clicked");
        var dropdownMenu = $('#profileDropdownMenu');
        var dropdownToggle = $(this);
        var offset = dropdownToggle.offset();
        dropdownMenu.css({
            top: offset.top + dropdownToggle.outerHeight(),
            left: offset.left
        }).toggleClass('show');
    });

    $(document).on('click', function(event) {
        if (!$(event.target).closest('#profileDropdown, #profileDropdownMenu').length) {
            $('#profileDropdownMenu').removeClass('show');
        }
    });
});


export function fetchNotificationCount() {
    return fetch('/api/notifications/', {
        method: 'GET',
        headers: {
            'Content-Type': 'application/json'
        }
    })
    .then(response => response.json())
    .then(data => {
        console.log('Notifications fetched for badge:', data); // Debugging log
        const notificationBadge = document.getElementById('notificationBadge');
        const unreadCount = data.notifications ? data.notifications.length : 0;

        console.log('Unread notification count:', unreadCount); // Debugging log

        if (unreadCount > 0) {
            notificationBadge.textContent = unreadCount; // Update the badge with the count
            notificationBadge.style.display = 'inline'; // Show the badge
            console.log('Badge updated and displayed with count:', unreadCount); // Debugging log
        } else {
            notificationBadge.style.display = 'none'; // Hide the badge if no unread notifications
            console.log('Badge hidden as there are no unread notifications'); // Debugging log
        }
    })
    .catch(error => {
        console.error('Error fetching notification count:', error);
    });
}

function fetchNotifications() {
    fetch('/api/notifications/', {
        method: 'GET',
        headers: {
            'Content-Type': 'application/json'
        }
    })
    .then(response => response.json())
    .then(data => {
        console.log('Notifications fetched for dropdown:', data); // Debugging log
        const notificationsList = document.getElementById('notificationsList');
        notificationsList.innerHTML = '';

        if (data.notifications && data.notifications.length > 0) {
            data.notifications.forEach(notification => {
                const notificationItem = document.createElement('p');
                notificationItem.className = 'dropdown-item';
                notificationItem.textContent = `${notification.message} (${notification.timestamp})`;
                notificationsList.appendChild(notificationItem);
            });
        } else {
            notificationsList.innerHTML = '<p class="dropdown-item text-muted">No new notifications</p>';
        }

        // Update the badge first
        fetchNotificationCount().then(() => {
            console.log('Badge updated after fetching notifications'); // Debugging log

            // Mark notifications as read after the badge is updated
            markNotificationsAsRead();
        });
    })
    .catch(error => {
        console.error('Error fetching notifications:', error);
        const notificationsList = document.getElementById('notificationsList');
        notificationsList.innerHTML = '<p class="dropdown-item text-danger">Error loading notifications</p>';
    });
}

function markNotificationsAsRead() {
    fetch('/api/notifications/mark-read/', {
        method: 'POST',
        headers: {
            'X-CSRFToken': '{{ csrf_token }}'
        }
    })
    .then(response => response.json())
    .then(data => {
        console.log("Notifications marked as read");
        fetchNotificationCount(); // Update the badge after marking notifications as read
    })
    .catch(error => console.error('Error marking notifications as read:', error));
}



document.getElementById('profileDropdown').addEventListener('click', function() {
    fetchNotifications(); // Fetch and display notifications when the dropdown is clicked
});

function updateNavbarHeight() {
    const navbar = document.querySelector(".navbar"); // Select the navbar
    if (navbar) {
        const navbarHeight = navbar.offsetHeight; // Get the height of the navbar
        document.documentElement.style.setProperty("--navbar-height", `${navbarHeight + 5}px`); // Set the CSS variable
    }
}

document.addEventListener("DOMContentLoaded", function () {
    // Fetch the notification count on page load
    fetchNotificationCount();

    // Dynamically set the --navbar-height CSS variable
    const navbar = document.querySelector(".navbar"); // Select the navbar
    if (navbar) {
        const navbarHeight = navbar.offsetHeight; // Get the height of the navbar
        document.documentElement.style.setProperty("--navbar-height", `${navbarHeight + 5}px`); // Set the CSS variable
    }
    updateNavbarHeight();
});

// Update the --navbar-height CSS variable on window resize
window.addEventListener("resize", updateNavbarHeight);
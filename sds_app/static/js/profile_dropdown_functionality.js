$(document).ready(function() {
    // Initialize all dropdowns
    $('.dropdown-toggle').dropdown();

    // Handle Requests Dropdown
    $('#requestsDropdown').on('click', function(e) {
        e.preventDefault();
        console.log('Requests dropdown clicked');
        $('.dropdown-menu').not('#requestsDropdownMenu').removeClass('show');
        var dropdownMenu = $('#requestsDropdownMenu');
        var dropdownToggle = $(this);
        var offset = dropdownToggle.offset();

        var topOffset = 40; // Adjust as needed
        var menuWidth = dropdownMenu.outerWidth();
        var toggleWidth = dropdownToggle.outerWidth();
        var windowWidth = $(window).width();

        // Default: align left edges
        var left = offset.left;

        // If the menu would overflow the right edge, align right edges
        if (left + menuWidth > windowWidth) {
            left = offset.left + toggleWidth - menuWidth;
            if (left < 0) left = 0;
        }

        dropdownMenu.css({
            position: 'absolute',
            top: offset.top + dropdownToggle.outerHeight() + topOffset,
            left: left
        }).toggleClass('show');
        console.log('Requests dropdown positioned at:', {
            top: offset.top + dropdownToggle.outerHeight() + topOffset,
            left: left
        });
    });

    // Handle Profile Dropdown with custom positioning
    $('#profileDropdown').on('click', function(e) {
        e.preventDefault();
        console.log('Profile dropdown clicked');
        $('.dropdown-menu').not('#profileDropdownMenu').removeClass('show');
        var dropdownMenu = $('#profileDropdownMenu');
        var dropdownToggle = $(this);
        var offset = dropdownToggle.offset();

        // Add a vertical offset for the profile dropdown
        var topOffset = 16; // Adjust this value as needed
        var leftOffset = 0; // Adjust if you want to shift horizontally

        dropdownMenu.css({
            position: 'absolute',
            top: offset.top + dropdownToggle.outerHeight() + topOffset,
            left: offset.left + leftOffset
        }).toggleClass('show');
        console.log('Profile dropdown positioned at:', {
            top: offset.top + dropdownToggle.outerHeight() + topOffset,
            left: offset.left + leftOffset
        });
        markNotificationsAsRead();
    });

    // Close dropdowns when clicking outside
    $(document).on('click', function(event) {
        if (!$(event.target).closest('#profileDropdown, #profileDropdownMenu, #requestsDropdown, .dropdown-menu').length) {
            $('.dropdown-menu').removeClass('show');
        }
    });
});

function fetchNotificationCount() {
    return fetch('/api/notifications/', {
        method: 'GET',
        headers: {
            'Content-Type': 'application/json'
        },
    })
    .then(response => response.json())
    .then(data => {
        // console.log('Notifications fetched for badge:', data);
        const notificationBadge = document.getElementById('notificationBadge');
        const unreadCount = data.notifications ? data.notifications.length : 0;

        if (unreadCount > 0) {
            notificationBadge.textContent = unreadCount;
            notificationBadge.style.display = 'inline';
        } else {
            notificationBadge.style.display = 'none';
        }
    })
    .catch(error => {
        console.error('Error fetching notification count:', error);
    });
}

function fetchNotifications() {
    return fetch('/api/notifications/', {
        method: 'GET',
        headers: {
            'Content-Type': 'application/json'
        },
        credentials: 'same-origin'
    })
    .then(response => {
        if (response.status === 401) {
            console.warn('User is not authenticated. Notifications cannot be fetched.');
            return;
        }
        if (!response.ok) {
            throw new Error(`HTTP error! status: ${response.status}`);
        }
        return response.json();
    })
    .then(data => {
        if (data) {
            // Get existing notifications from sessionStorage
            const storedNotifications = sessionStorage.getItem('notifications');
            const existingNotifications = storedNotifications ? JSON.parse(storedNotifications) : [];

            // Merge new notifications with existing ones
            const mergedNotifications = [...data.notifications, ...existingNotifications];

            // Remove duplicates (if notifications have unique IDs)
            const uniqueNotifications = mergedNotifications.filter((notification, index, self) =>
                index === self.findIndex(n => n.id === notification.id)
            );

            // Save merged notifications back to sessionStorage
            sessionStorage.setItem('notifications', JSON.stringify(uniqueNotifications));

            // Update the dropdown
            const notificationsList = document.getElementById('notificationsList');
            notificationsList.innerHTML = '';

            if (uniqueNotifications.length > 0) {
                uniqueNotifications.forEach(notification => {
                    const notificationItem = document.createElement('p');
                    notificationItem.className = 'dropdown-item';
                    notificationItem.textContent = `${notification.message} (${notification.timestamp})`;
                    notificationsList.appendChild(notificationItem);
                });
            } else {
                notificationsList.innerHTML = '<p class="dropdown-item text-muted">No new notifications</p>';
            }

            // Update the notification badge without making a call to fetchNotificationCount
            const notificationBadge = document.getElementById('notificationBadge');
            const unreadCount = uniqueNotifications.length;

            if (unreadCount > 0) {
                notificationBadge.textContent = unreadCount;
                notificationBadge.style.display = 'inline';
            } else {
                notificationBadge.style.display = 'none';
            }
            
        }
    })
    .catch(error => {
        console.error('Error fetching notifications:', error);
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
        // console.log("Notifications marked as read");
        fetchNotificationCount(); // Update the badge after marking notifications as read
    })
    .catch(error => console.error('Error marking notifications as read:', error));
}


// Example: Attach event listener for dropdown
document.getElementById('profileDropdown').addEventListener('click', function() {
    markNotificationsAsRead(); // Fetch and display notifications when the dropdown is clicked
});

function updateNavbarHeight() {
    const navbar = document.querySelector(".navbar"); // Select the navbar
    if (navbar) {
        const navbarHeight = navbar.offsetHeight; // Get the height of the navbar
        document.documentElement.style.setProperty("--navbar-height", `${navbarHeight + 5}px`); // Set the CSS variable
    }
}


document.addEventListener("DOMContentLoaded", function () {

    fetchNotifications(); // Fetch and update the notification badge on page load

    // Dynamically set the --navbar-height CSS variable
    const navbar = document.querySelector(".navbar"); // Select the navbar
    if (navbar) {
        const navbarHeight = navbar.offsetHeight; // Get the height of the navbar
        document.documentElement.style.setProperty("--navbar-height", `${navbarHeight + 5}px`); // Set the CSS variable
    }
    updateNavbarHeight();
});

// Attach to the global window object
window.fetchNotifications = fetchNotifications;

// Update the --navbar-height CSS variable on window resize
window.addEventListener("resize", updateNavbarHeight);
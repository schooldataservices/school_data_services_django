// To allow the main container to expand when the TOC is hidden
document.addEventListener("DOMContentLoaded", function () {
    var tocContainer = document.querySelector(".toc-container");
    var contentWrapper = document.querySelector(".content-wrapper");
    var tocToggle = document.getElementById("toc-toggle");

    // Dynamically set the initial state based on screen size
    function setInitialState() {
        if (window.innerWidth <= 767) {
            // Mobile view: Start with TOC hidden
            tocContainer.classList.add("hidden");
            tocContainer.classList.remove("open");
            contentWrapper.style.marginLeft = "0px"; // No margin for mobile view
        } else {
            // Non-mobile view: Start with TOC open
            tocContainer.classList.add("open");
            tocContainer.classList.remove("hidden");
            contentWrapper.style.marginLeft = "150px"; // Adjust margin for desktop view
        }

        // Ensure the toggle button is always visible
        adjustButtonPosition();
    }

    // Adjust the button's position dynamically
    function adjustButtonPosition() {
        if (tocContainer) {
            var tocRect = tocContainer.getBoundingClientRect(); // Get the TOC's position and dimensions

        }
    }

    // Call the function to set the initial state
    setInitialState();

    // Adjust dynamically on window resize
    window.addEventListener("resize", function () {
        setInitialState();
    });

    // Toggle the TOC visibility on button click
    tocToggle.addEventListener("click", function () {
        if (tocContainer.classList.contains("hidden")) {
            // Show the TOC
            tocContainer.classList.remove("hidden");
            tocContainer.classList.add("open");
            contentWrapper.style.marginLeft = "150px"; // Adjust margin when TOC is visible
        } else {
            // Hide the TOC
            tocContainer.classList.remove("open");
            tocContainer.classList.add("hidden");
            contentWrapper.style.marginLeft = "0px"; // Adjust margin when TOC is collapsed
        }

        // Ensure the toggle button stays in position
        adjustButtonPosition();
    });

    // Adjust the button position on page load
    adjustButtonPosition();

    // Adjust the button position when the TOC changes
    window.addEventListener("resize", adjustButtonPosition);

    // Adjust dynamically when subsections are toggled
    document.querySelectorAll(".toggle-btn-internal").forEach(function (button) {
        button.addEventListener("click", function () {
            setTimeout(adjustButtonPosition, 150); // Delay to allow the TOC height to update
        });
    });
});


function toggleSubsections(button) {
    const subList = button.nextElementSibling; // Get the next sibling (the sub-list)
    if (subList.style.display === "none") {
        subList.style.display = "block"; // Show the subsections
        button.textContent = "▼"; // Change icon to down arrow
    } else {
        subList.style.display = "none"; // Hide the subsections
        button.textContent = "▼"; // Change icon to right arrow
    }
}

function positionTocContainer() {
    var navbar = document.querySelector('.navbar');
    var tocContainer = document.querySelector('.toc-container');
    if (navbar && tocContainer) {
        var height = navbar.offsetHeight;
        tocContainer.style.top = height + 'px';
    }
}

// Call on load and resize
document.addEventListener("DOMContentLoaded", function () {
    positionTocContainer();
    window.addEventListener('resize', positionTocContainer);
});
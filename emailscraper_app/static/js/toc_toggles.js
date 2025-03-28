// To allow the main container to expand when the toggle is closed
document.addEventListener("DOMContentLoaded", function () {
    var tocContainer = document.querySelector(".toc-container");
    var contentWrapper = document.querySelector(".content-wrapper");
    var tocToggle = document.getElementById("toc-toggle");

    // Dynamically set the initial state based on screen size
    function setInitialState() {
        if (window.innerWidth <= 767) {
            // Mobile view: Start with 'hidden'
            tocContainer.classList.add("hidden");
            tocContainer.classList.remove("open");
            contentWrapper.style.marginLeft = "0px"; // No margin for mobile view
        } else {
            // Non-mobile view: Start with 'open'
            tocContainer.classList.add("open");
            tocContainer.classList.remove("hidden");
            contentWrapper.style.marginLeft = "150px"; // Adjust margin for desktop view
        }
    }

    // Call the function to set the initial state
    setInitialState();

    // Optional: Adjust dynamically on window resize
    window.addEventListener("resize", function () {
        setInitialState();
    });

    // Toggle the TOC visibility on button click
    tocToggle.addEventListener("click", function () {
        if (tocContainer.classList.contains("hidden")) {
            // Remove 'hidden' and add 'open' to show the TOC
            tocContainer.classList.remove("hidden");
            tocContainer.classList.add("open");
            contentWrapper.style.marginLeft = "150px"; // Adjust margin when TOC is visible
        } else {
            // Remove 'open' and add 'hidden' to hide the TOC
            tocContainer.classList.remove("open");
            tocContainer.classList.add("hidden");
            contentWrapper.style.marginLeft = "0px"; // Adjust margin when TOC is collapsed
        }
    });
});
// Dynamically set the toggle button based on navbar location
    document.addEventListener("DOMContentLoaded", function () {
        var tocToggle = document.getElementById('toc-toggle');
        var navbar = document.querySelector('.navbar'); // Assuming you have a navbar

        // Adjust the button's position based on the navbar height
        function adjustButtonPosition() {
            var navbarHeight = navbar ? navbar.offsetHeight : 0;
            tocToggle.style.top = (navbarHeight + 305) + 'px'; // 20px below the navbar
            tocToggle.style.left = '5px'; // 20px from the left
        }

        // Set the initial position
        adjustButtonPosition();

        // Adjust the position on window resize
        window.addEventListener('resize', adjustButtonPosition);
    });
// Priority Filter Logic
document.getElementById("priorityFilter").addEventListener("change", function() {
    // console.log("Priority filter changed to:", this.value);
    applyFilters();
});

// Date Filter Logic
document.getElementById("dateFilter").addEventListener("change", function() {
    // console.log("Date filter changed to:", this.value);
    applyFilters();
});

// Completion Filter Logic
document.getElementById("completionFilter").addEventListener("change", function() {
    // console.log("Completion filter changed to:", this.value);
    applyFilters();
});


function applyFilters() {
    let selectedPriority = document.getElementById("priorityFilter").value.toLowerCase();
    let selectedDate = document.getElementById("dateFilter").value.toLowerCase();
    let selectedCompletion = document.getElementById("completionFilter").value.toLowerCase();
    let rows = document.querySelectorAll("table tbody tr");

    // console.log("Applying filters: ", { selectedPriority, selectedDate, selectedCompletion });

    rows.forEach(row => {
        let priorityElement = row.children[1]; // Priority column
        let dateElement = row.children[0]; // Date Submitted column
        let scheduleElement = row.children[2]; // Schedule Time column
        let completionElement = row.children[4]; // Completion Status column

        if (!priorityElement || !dateElement || !scheduleElement || !completionElement) return;

        let priority = priorityElement.textContent.trim().toLowerCase();
        let scheduleTime = new Date(scheduleElement.textContent.trim());
        let completionStatus = completionElement.textContent.trim().toLowerCase();

        if (isNaN(scheduleTime)) {
            console.warn("Invalid date:", scheduleElement.textContent);
            return;
        }

        let completionValue = completionStatus.includes("completed") ? "true" : "false";

        let dateMatch = isDateMatch(selectedDate, scheduleTime);
        let statusMatch = selectedCompletion === "all" || completionValue === selectedCompletion;

        if ((selectedPriority === "all" || priority === selectedPriority) && dateMatch && statusMatch) {
            row.style.display = "";
        } else {
            row.style.display = "none";
        }
    });
}

function isDateMatch(selectedDate, scheduleTime) {
    if (selectedDate === "today") {
        let today = new Date();
        today.setHours(0, 0, 0, 0);
        return scheduleTime.toDateString() === today.toDateString();
    } else if (selectedDate === "last7days") {
        let last7Days = new Date();
        last7Days.setDate(last7Days.getDate() - 7);
        return scheduleTime >= last7Days;
    } else if (selectedDate === "thismonth") {
        let firstDayOfMonth = new Date(new Date().getFullYear(), new Date().getMonth(), 1);
        return scheduleTime >= firstDayOfMonth;
    }
    return true;
}



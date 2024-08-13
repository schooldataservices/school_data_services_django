$(document).ready(function() {
    var maxRows = 10; // Initial row limit

    // Function to update the hidden input field
    function updateSelectedFileUrl() {
        var fileUrl = $('#file-select').find(':selected').data('url');
        $('#selected-file-url').val(fileUrl);
    }

    // Function to fetch and display the file content
    function loadFileContent(fileUrl) {
        if (fileUrl) {
            fetch(fileUrl)
                .then(response => {
                    if (!response.ok) {
                        throw new Error('Network response was not ok.');
                    }
                    return response.text();
                })
                .then(data => {
                    var rows = data.split('\n');
                    var table = '<table class="table table-bordered">';
                    
                    // Limit the number of rows
                    var numRows = Math.min(rows.length, maxRows);
                    
                    for (var i = 0; i < numRows; i++) {
                        var row = rows[i];
                        var columns = row.split(',');
                        table += '<tr>';
                        columns.forEach(col => {
                            if (i === 0) {
                                table += '<th>' + col.trim() + '</th>';
                            } else {
                                table += '<td>' + col.trim() + '</td>';
                            }
                        });
                        table += '</tr>';
                    }
                    
                    table += '</table>';
                    $('#file-content').html(table);
                    $('#row-limit-display').text('Showing ' + numRows + ' rows');
                })
                .catch(error => {
                    console.error('Error fetching the file:', error);
                    $('#file-content').html('Error loading file content.');
                });
        } else {
            $('#file-content').html('No file selected.');
        }
    }

    // Handle download button click
    $('#download-button').click(function() {
        var fileUrl = $('#file-select').find(':selected').data('url');
        if (fileUrl) {
            window.location.href = fileUrl;
        } else {
            alert('No file selected.');
        }
    });

    // Handle update button click
    $('#update-file-button').click(function() {
        var pk = $('#file-select').val();
        if (pk) {
            var updateUrl = "/email/" + pk + "/update/";
            window.location.href = updateUrl;
        } else {
            alert('No file selected.');
        }
    });

    // Handle file selection change
    $('#file-select').change(function() {
        var fileUrl = $(this).find(':selected').data('url');
        $('#delete-file-form').attr('action', '/email/' + $(this).val() + '/delete/');
        
        // Update the hidden input field with the selected file URL
        updateSelectedFileUrl();

        // Fetch and display the file content
        loadFileContent(fileUrl);
    });

    // Handle increase row button click
    $('#increase-rows').click(function() {
        maxRows += 10; // Increase row limit by 10
        var fileUrl = $('#file-select').find(':selected').data('url');
        if (fileUrl) {
            loadFileContent(fileUrl);
        }
    });

    // Handle decrease row button click
    $('#decrease-rows').click(function() {
        if (maxRows > 10) { // Ensure a minimum of 10 rows
            maxRows -= 10; // Decrease row limit by 10
            var fileUrl = $('#file-select').find(':selected').data('url');
            if (fileUrl) {
                loadFileContent(fileUrl);
            }
        }
    });

    // Set the initial value of the hidden input field and load the file content
    var initialFileUrl = $('#file-select').find(':selected').data('url');
    if (initialFileUrl) {
        updateSelectedFileUrl();
        loadFileContent(initialFileUrl);
    }
});

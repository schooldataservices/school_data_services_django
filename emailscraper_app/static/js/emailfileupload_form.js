$(document).ready(function() {
    $('#download-button').click(function() {
        var fileUrl = $('#file-select').find(':selected').data('url');
        if (fileUrl) {
            window.location.href = fileUrl;
        } else {
            alert('No file selected.');
        }
    });

    $('#update-file-button').click(function() {
        var pk = $('#file-select').val();
        if (pk) {
            var updateUrl = "/email/" + pk + "/update/";
            window.location.href = updateUrl;
        } else {
            alert('No file selected.');
        }
    });

    $('#file-select').change(function() {
        var fileUrl = $(this).find(':selected').data('url');
        $('#delete-file-form').attr('action', '/email/' + $(this).val() + '/delete/');

        // Fetch and display the file content
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
                    rows.forEach((row, index) => {
                        var columns = row.split(',');
                        table += '<tr>';
                        columns.forEach(col => {
                            if (index === 0) {
                                table += '<th>' + col.trim() + '</th>';
                            } else {
                                table += '<td>' + col.trim() + '</td>';
                            }
                        });
                        table += '</tr>';
                    });
                    table += '</table>';
                    $('#file-content').html(table);
                })
                .catch(error => {
                    console.error('Error fetching the file:', error);
                    $('#file-content').html('Error loading file content.');
                });
        } else {
            $('#file-content').html('No file selected.');
        }
    });
});

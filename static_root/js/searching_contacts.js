$(document).ready(function () {
    var searchUrl = $('#search-contact').data('search-url');
    var detailsUrl = $('#search-contact').data('details-url');

    function searchContacts(query) {
        if (query.length > 2) {
            $.ajax({
                url: searchUrl,
                data: {
                    'q': query
                },
                success: function (data) {
                    var suggestions = $('#contact-suggestions');
                    suggestions.empty().show();
                    data.forEach(function (contact) {
                        suggestions.append('<a class="dropdown-item" href="#" data-contact-id="' + contact.id + '">' + contact.name + '</a>');
                    });
                    console.log("Suggestions: ", suggestions.html());  // Check the rendered HTML

                },
                error: function (xhr, status, error) {
                    console.error("Search AJAX error: ", status, error);
                }
            });
        } else {
            $('#contact-suggestions').hide();
        }
    }

    // Trigger search when typing in the input field
    $('#search-contact').on('input', function () {
        var query = $(this).val();
        searchContacts(query);
    });

    // Trigger search manually when clicking the button
    $('#search-button').on('click', function (e) {
        e.preventDefault();
        var query = $('#search-contact').val();
        searchContacts(query);
    });

    // When a contact is selected, populate the form
    $('#contact-suggestions').on('click', '.dropdown-item', function (e) {
        e.preventDefault();
        var contactId = $(this).data('contact-id');

        $.ajax({
            url: detailsUrl,
            data: {
                'id': contactId
            },
            success: function (data) {
                // Assuming data contains fields that match your model/form field names
                $('#id_contact').val(data.contact);
                $('#id_company').val(data.company);
                $('#id_title').val(data.title);
                $('#id_department').val(data.department);
                $('#id_salutation').val(data.salutation); // Make sure salutation is handled correctly
                $('#id_phone').val(data.phone);
                $('#id_mobile').val(data.mobile);
                $('#id_email').val(data.email);
                $('#id_address').val(data.address);
                $('#id_city').val(data.city);
                $('#id_state').val(data.state);
                $('#id_ZIP').val(data.ZIP);  // Match case of 'ZIP'
                $('#id_county').val(data.county);
                $('#id_fax').val(data.fax);
                $('#id_web_site').val(data.web_site);
                $('#id_notes').val(data.notes);
            },
            error: function (xhr, status, error) {
                console.error("Details AJAX error: ", status, error);
            }
        });
    });
});

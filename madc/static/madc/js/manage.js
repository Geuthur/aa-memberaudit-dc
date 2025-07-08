/* global MaDCSettings */

$(document).ready(function() {
    // Extract CSRF token from MaDCSettings.csrfToken HTML
    function getCsrfToken() {
        if (MaDCSettings && MaDCSettings.csrfToken) {
            // Parse the HTML to get the value attribute
            const parser = new DOMParser();
            const doc = parser.parseFromString(MaDCSettings.csrfToken, 'text/html');
            const input = doc.querySelector('input[name="csrfmiddlewaretoken"]');
            return input ? input.value : '';
        }
        return '';
    }

    const csrfToken = getCsrfToken();

    const skillListTableVar = $('#skill-list-table');
    // Initialisierung der DataTable
    const tableSkilllist = skillListTableVar.DataTable({
        ajax: {
            url: MaDCSettings.urls.administration,
            type: 'GET',
            dataSrc: function (data) {
                return Object.values(data);
            },
            error: function (xhr, error, thrown) {
                console.error('Error loading data:', error);
                tableSkilllist.clear().draw();
            }
        },
        columns: [
            {
                data: 'name',
                render: {
                    display: 'html',
                    sort: 'sort',
                }
            },
            {
                data: 'skills',
                render: function (data, type) {
                    return data;
                }
            },
            {
                data: 'active',
                render: {
                    display: 'html',
                    sort: 'sort',
                }
            },
            {
                data: 'ordering',
                render: {
                    display: 'html',
                    sort: 'sort',
                }
            },
            {
                data: 'category',
                render: {
                    display: 'html',
                    sort: 'sort',
                }
            },
            {
                data: 'actions',
                className: 'd-flex justify-content-end',
                render: function (data, type) {
                    return data.delete;
                }
            },
        ],
        columnDefs: [
            {
                targets: [1, 5],
                sortable: false,
            },
        ],
        order: [[0, 'asc']],
    });

    tableSkilllist.on('draw', function (row, data) {
        $('[data-tooltip-toggle="doctrine-tooltip"]').tooltip({
            trigger: 'hover',
        });

        // Initialize x-editable for all editable elements
        $('.editable').editable({
            mode: 'inline',
            emptytext: 'Click to edit',
            ajaxOptions: {
                type: 'POST',
                beforeSend: function(xhr, settings) {
                    // Set CSRF token in header
                    xhr.setRequestHeader('X-CSRFToken', csrfToken);
                },
                complete: function(xhr, textStatus) {
                    console.log('Response:', xhr.responseText);
                }
            },
            success: function(response, newValue) {
                tableSkilllist.ajax.reload();
            },
            error: function(xhr, status, error) {
                // Parse JSON response to get the message
                let errorMessage = 'Update failed';
                try {
                    const response = JSON.parse(xhr.responseText);
                    errorMessage = response.message || 'Update failed';
                } catch (e) {
                    errorMessage = xhr.responseText || error;
                }

                return errorMessage;
            }
        });

        // Initialize boolean editable (active/inactive)
        $('.editable-boolean').editable({
            mode: 'inline',
            emptytext: 'Click to edit',
            ajaxOptions: {
                type: 'POST',
                beforeSend: function(xhr, settings) {
                    // Set CSRF token in header
                    xhr.setRequestHeader('X-CSRFToken', csrfToken);
                },
                complete: function(xhr, textStatus) {
                    tableSkilllist.ajax.reload();
                }
            },
            success: function(response, newValue) {
                console.log('Updated active status:', newValue);
                tableSkilllist.ajax.reload();
            },
            error: function(xhr, status, error) {
                // Parse JSON response to get the message
                let errorMessage = 'Update failed';
                try {
                    const response = JSON.parse(xhr.responseText);
                    errorMessage = response.message || 'Update failed';
                } catch (e) {
                    errorMessage = xhr.responseText || error;
                }

                return errorMessage;
            }
        });
    });
});

/* global MaDCSettings, allTableData, tableSkilllist, populateCategoryFilter, filterByCategories, filterDoctrineItems, ClipboardJS */

// Global variables for cross-file access
window.allTableData = [];
window.tableSkilllist = null;

$(document).ready(function() {
    const skillListTableVar = $('#skill-checker-table');

    const tableSkilllist = skillListTableVar.DataTable({
        ajax: {
            url: MaDCSettings.urls.skillChecker,
            type: 'GET',
            dataSrc: function (data) {
                const filteredData = data.filter(character => {
                    return character.doctrines && Object.keys(character.doctrines).length > 0;
                });

                // Store all data for category filtering (make it global)
                window.allTableData = filteredData;

                // Populate category filter dropdown
                populateCategoryFilter(filteredData);

                return filteredData;
            },
            error: function (xhr, error, thrown) {
                console.error('Error loading data:', error);
                tableSkilllist.clear().draw();
            }
        },
        columns: [
            {
                data: 'character',
                render: function (data, type) {
                    if (type === 'display') {
                        return `<img width="32" height="32" class="rounded-circle" src="https://images.evetech.net/characters/${data.character_id}/portrait?size=256"> ${data.character_name}`;
                    }
                    return data.character_name;
                }
            },
            {
                data: 'doctrines',
                render: function (data, type, row) {
                    if (type === 'display') {
                        // Convert doctrines object to array and sort by order
                        const doctrineArray = Object.entries(data).map(([doctrineName, doctrine]) => ({
                            name: doctrineName,
                            doctrine: doctrine,
                            order: doctrine.order || 999 // Default high order for items without order
                        }));

                        // Sort by order (ascending)
                        doctrineArray.sort((a, b) => a.order - b.order);

                        // Render sorted doctrines as a list of divs with flex layout
                        let html = '<div class="d-flex flex-wrap gap-2">';
                        doctrineArray.forEach(({ name, doctrine }) => {
                            // Add category information to the HTML if it exists
                            let doctrineHtml = doctrine.html || name;
                            if (doctrine.category) {
                                doctrineHtml = doctrineHtml.replace(
                                    'data-doctrine="' + name + '"',
                                    'data-doctrine="' + name + '" data-category="' + doctrine.category + '"'
                                );
                            }
                            html += doctrineHtml;
                        });
                        html += '</div>';
                        return html;
                    }
                    return Object.keys(data).join(' ');
                }
            },
        ],
        columnDefs: [
            {
                targets: 0,
                searchable: false, // Disable searching on character names
            },
        ],
        order: [
            [0, 'asc']
        ],
        pageLength: 25,
    });

    // Make tableSkilllist globally accessible
    window.tableSkilllist = tableSkilllist;

    // Listen for search input changes
    $(document).on('keyup', '.dataTables_filter input', function() {
        setTimeout(filterDoctrineItems, 100);
    });

    // Also filter when search is cleared
    $(document).on('search', '.dataTables_filter input', function() {
        setTimeout(filterDoctrineItems, 100);
    });

    tableSkilllist.on('draw', function() {
        $('[data-tooltip-toggle="madc-tooltip"]').tooltip({
            trigger: 'hover',
        });

        // Apply current filter after table redraw
        setTimeout(filterDoctrineItems, 100);

        // Add clipboard functionality for missing skills (red buttons)
        setTimeout(() => {
            $('.doctrine-item').each(function() {
                const doctrineDiv = $(this);
                const copyButton = doctrineDiv.find('button[id^="copy-"]');

                if (copyButton.length && copyButton.hasClass('btn-danger')) {
                    const doctrineName = doctrineDiv.attr('data-doctrine');
                    const doctrineHtml = doctrineDiv.html();

                    // Find the doctrine data from the table row
                    const row = doctrineDiv.closest('tr');
                    const rowData = tableSkilllist.row(row).data();

                    if (rowData && rowData.doctrines && rowData.doctrines[doctrineName]) {
                        const doctrine = rowData.doctrines[doctrineName];
                        const missingSkills = [];

                        if (doctrine.skills) {
                            Object.keys(doctrine.skills).forEach(skillName => {
                                const skillLevel = doctrine.skills[skillName];
                                missingSkills.push(`${skillName} ${skillLevel}`);
                            });
                        }

                        const clipboardText = missingSkills.join('\n');
                        copyButton.attr('data-clipboard-text', clipboardText);

                        // Initialize ClipboardJS if not already initialized
                        if (!copyButton.data('clipboard-initialized')) {
                            new ClipboardJS(copyButton[0]).on('success', function(e) {
                                const originalIcon = copyButton.html();
                                const originalClass = copyButton.attr('class');

                                copyButton.html('<i class="fa-solid fa-check"></i>');
                                copyButton.removeClass('btn-danger').addClass('btn-success');

                                setTimeout(() => {
                                    copyButton.html(originalIcon);
                                    copyButton.attr('class', originalClass);
                                }, 1500);

                                e.clearSelection();
                            });

                            copyButton.data('clipboard-initialized', true);
                        }
                    }
                }
            });
        }, 100);
    });
});

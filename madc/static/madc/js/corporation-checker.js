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

                // Replace fa-copy icons with fa-circle icons after data load
                setTimeout(() => {
                    $('.fa-copy').removeClass('fa-copy').addClass('fa-circle');
                }, 100);

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
                render: function (data, type, row) {
                    if (type === 'display') {
                        let infoIcon = '';

                        if (row.alts && row.alts.length > 0) {
                            const altsContent = row.alts.map(alt =>
                                `<div class="d-flex align-items-center mb-1">
                                    <img width="24" height="24" class="rounded-circle me-2" src="https://images.evetech.net/characters/${alt.character_id}/portrait?size=256">
                                    <span>${alt.character_name}</span>
                                </div>`
                            ).join('');

                            // Escape HTML properly for data attribute
                            const escapedContent = altsContent.replace(/"/g, '&quot;').replace(/'/g, '&#39;');

                            infoIcon = `<i class="fa-solid fa-circle-question fa-fw ms-2 alt-info-icon"
                                          data-character-id="${data.character_id}"
                                          data-alts-content="${escapedContent}"
                                          style="cursor: pointer;"></i>`;
                        }

                        return `
                            <img width="32" height="32" class="rounded-circle" src="https://images.evetech.net/characters/${data.character_id}/portrait?size=256">
                            ${data.character_name}
                            ${infoIcon}
                        `;
                    }
                    // For sorting/filtering, return character name and alt names
                    const altNames = row.alts ? row.alts.map(alt => alt.character_name).join(' ') : '';
                    return `${data.character_name} ${altNames}`;
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
                searchable: true, // Enable searching on character names (including alts)
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

        // Initialize Bootstrap popovers for alt characters
        $('.alt-info-icon').each(function() {
            const $icon = $(this);
            const altsContent = $icon.data('alts-content');

            $icon.popover({
                trigger: 'hover',
                html: true,
                placement: 'right',
                title: 'Alt Characters',
                content: altsContent,
                sanitize: false
            });
        });

        // Close other popovers when opening a new one
        $('.alt-info-icon').on('shown.bs.popover', function() {
            $('.alt-info-icon').not(this).popover('hide');
        });

        // Replace fa-copy icons with fa-circle icons
        $('.fa-copy').removeClass('fa-copy').addClass('fa-xmark');

        // Apply current filter after table redraw
        setTimeout(filterDoctrineItems, 100);
    });
});

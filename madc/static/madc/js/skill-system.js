// Function to filter data by selected categories
function filterByCategories(selectedCategories) {
    const allTableData = window.allTableData;
    const tableSkilllist = window.tableSkilllist;

    if (!tableSkilllist || !allTableData) {
        console.error('Table or data not initialized');
        return;
    }

    let filteredData = allTableData;

    if (selectedCategories.length > 0) {
        filteredData = allTableData.filter(character => {
            if (!character.doctrines) return false;

            // Check if character has any doctrines with any of the selected categories
            return Object.values(character.doctrines).some(doctrine => {
                return selectedCategories.some(selectedCategory => {
                    if (selectedCategory === 'No Category') {
                        return !doctrine.category || doctrine.category === null;
                    }
                    return doctrine.category === selectedCategory;
                });
            });
        });

        // Also filter the doctrines within each character to only show the selected categories
        filteredData = filteredData.map(character => {
            const filteredDoctrines = {};

            Object.entries(character.doctrines).forEach(([doctrineName, doctrine]) => {
                const shouldInclude = selectedCategories.some(selectedCategory => {
                    if (selectedCategory === 'No Category') {
                        return !doctrine.category || doctrine.category === null;
                    }
                    return doctrine.category === selectedCategory;
                });

                if (shouldInclude) {
                    filteredDoctrines[doctrineName] = doctrine;
                }
            });

            return {
                ...character,
                doctrines: filteredDoctrines
            };
        });
    }

    // Clear and reload table with filtered data
    tableSkilllist.clear().rows.add(filteredData).draw();
}

// Function to populate category filter checkboxes
function populateCategoryFilter(data) {
    const categorySet = new Set();

    data.forEach(character => {
        if (character.doctrines) {
            Object.values(character.doctrines).forEach(doctrine => {
                if (doctrine.category) {
                    categorySet.add(doctrine.category);
                } else {
                    categorySet.add('No Category');
                }
            });
        }
    });

    const categoryFilter = $('#category-filter');
    // Keep the "All Categories" checkbox and remove other checkboxes
    const currentCheckboxes = categoryFilter.find('.form-check:not(:first-child)');
    currentCheckboxes.remove();

    // Sort categories with "No Category" first, then alphabetically
    const sortedCategories = Array.from(categorySet).sort((a, b) => {
        if (a === 'No Category') return -1;
        if (b === 'No Category') return 1;
        return a.localeCompare(b);
    });

    sortedCategories.forEach((category, index) => {
        const checkboxId = `category-${index}`;
        const checkboxHtml = `
            <div class="form-check">
                <input class="form-check-input category-checkbox" type="checkbox" value="${category}" id="${checkboxId}">
                <label class="form-check-label" for="${checkboxId}">
                    ${category}
                </label>
            </div>
        `;
        categoryFilter.append(checkboxHtml);
    });

    // Add event listeners for checkboxes
    $('.category-checkbox').on('change', function() {
        const selectedCategories = [];
        $('.category-checkbox:checked').each(function() {
            selectedCategories.push($(this).val());
        });

        // Handle "All Categories" checkbox
        const allCategoriesCheckbox = $('#all-categories');
        if (selectedCategories.length === 0) {
            allCategoriesCheckbox.prop('checked', true);
            filterByCategories([]);
        } else {
            allCategoriesCheckbox.prop('checked', false);
            filterByCategories(selectedCategories);
        }
    });

    // Handle "All Categories" checkbox
    $('#all-categories').on('change', function() {
        if ($(this).is(':checked')) {
            $('.category-checkbox').prop('checked', false);
            filterByCategories([]);
        }
    });
}

// Custom function to filter doctrine items based on search
function filterDoctrineItems() {
    const searchValue = $('.dataTables_filter input').val().toLowerCase();

    $('.doctrine-item').each(function() {
        const doctrineName = $(this).attr('data-doctrine').toLowerCase();

        if (!searchValue || doctrineName.includes(searchValue)) {
            $(this).show();
        } else {
            $(this).hide();
        }
    });
}

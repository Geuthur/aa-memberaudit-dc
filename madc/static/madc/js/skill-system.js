// Function to filter data by category
function filterByCategory(selectedCategory) {
    const allTableData = window.allTableData;
    const tableSkilllist = window.tableSkilllist;

    if (!tableSkilllist || !allTableData) {
        console.error('Table or data not initialized');
        return;
    }

    let filteredData = allTableData;

    if (selectedCategory) {
        filteredData = allTableData.filter(character => {
            if (!character.doctrines) return false;

            // Check if character has any doctrines with the selected category
            return Object.values(character.doctrines).some(doctrine => {
                if (selectedCategory === 'No Category') {
                    return !doctrine.category || doctrine.category === null;
                }
                return doctrine.category === selectedCategory;
            });
        });

        // Also filter the doctrines within each character to only show the selected category
        filteredData = filteredData.map(character => {
            const filteredDoctrines = {};

            Object.entries(character.doctrines).forEach(([doctrineName, doctrine]) => {
                if (selectedCategory === 'No Category') {
                    if (!doctrine.category || doctrine.category === null) {
                        filteredDoctrines[doctrineName] = doctrine;
                    }
                } else if (doctrine.category === selectedCategory) {
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

// Function to populate category filter dropdown
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
    // Keep the "All Categories" option and add unique categories
    const currentOptions = categoryFilter.find('option:not([value=""])');
    currentOptions.remove();

    // Sort categories with "No Category" first, then alphabetically
    const sortedCategories = Array.from(categorySet).sort((a, b) => {
        if (a === 'No Category') return -1;
        if (b === 'No Category') return 1;
        return a.localeCompare(b);
    });

    sortedCategories.forEach(category => {
        categoryFilter.append(`<option value="${category}">${category}</option>`);
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

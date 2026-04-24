// Task Search - Handles search and filtering
function taskSearch() {
    return {
        expanded: false,
        simpleSearch: '',
        filters: {
            title: '',
            description: '',
            status: {
                open: false,
                waiting: false,
                deferred: false,
                declined: false,
                stale: false
            },
            activeStatus: 'all', // 'active', 'all', 'inactive'
            completionStatus: 'incomplete' // 'incomplete', 'all', 'complete'
        },

        expand() {
            // When expanding, split simple search into title field
            if (this.simpleSearch) {
                this.filters.title = this.simpleSearch;
            }
            this.expanded = true;
        },

        collapse() {
            this.expanded = false;
        },

        applySimpleSearch() {
            console.log('Simple search:', this.simpleSearch);
            // TODO: Trigger search with simpleSearch value
            // This would search both title and description
            alert('Searching for: "' + this.simpleSearch + '" (Demo - no actual search)');
        },

        applyFilters() {
            console.log('Applying filters:', this.filters);

            // Build filter summary
            const summary = this.getFilterSummary();

            // TODO: Trigger filtered search with filters object
            alert('Filters applied:\n' + summary + '\n\n(Demo - no actual search)');

            // Collapse back to simple view
            this.collapse();
        },

        clearFilters() {
            this.simpleSearch = '';
            this.filters = {
                title: '',
                description: '',
                status: {
                    open: false,
                    waiting: false,
                    deferred: false,
                    declined: false,
                    stale: false
                },
                activeStatus: 'all',
                completionStatus: 'incomplete'
            };

            console.log('Filters cleared');
        },

        hasActiveFilters() {
            // Check if any filters are set
            if (this.simpleSearch) return true;
            if (this.filters.title) return true;
            if (this.filters.description) return true;

            // Check if any status checkboxes are checked
            const hasStatusFilter = Object.values(this.filters.status).some(v => v === true);
            if (hasStatusFilter) return true;

            // Check if non-default radio options are selected
            if (this.filters.activeStatus !== 'all') return true;
            if (this.filters.completionStatus !== 'incomplete') return true;

            return false;
        },

        getActiveFilterCount() {
            let count = 0;

            if (this.simpleSearch) count++;
            if (this.filters.title) count++;
            if (this.filters.description) count++;

            // Count status filters
            count += Object.values(this.filters.status).filter(v => v === true).length;

            if (this.filters.activeStatus !== 'all') count++;
            if (this.filters.completionStatus !== 'incomplete') count++;

            return count;
        },

        getFilterSummary() {
            const parts = [];

            if (this.filters.title) {
                parts.push('Title contains: "' + this.filters.title + '"');
            }

            if (this.filters.description) {
                parts.push('Description contains: "' + this.filters.description + '"');
            }

            const selectedStatuses = Object.entries(this.filters.status)
                .filter(([key, value]) => value === true)
                .map(([key, value]) => key);

            if (selectedStatuses.length > 0) {
                parts.push('Status: ' + selectedStatuses.join(', '));
            }

            if (this.filters.activeStatus !== 'all') {
                parts.push('Active: ' + this.filters.activeStatus);
            }

            if (this.filters.completionStatus !== 'incomplete') {
                parts.push('Completion: ' + this.filters.completionStatus);
            }

            return parts.length > 0 ? parts.join('\n') : 'No filters active';
        }
    };
}
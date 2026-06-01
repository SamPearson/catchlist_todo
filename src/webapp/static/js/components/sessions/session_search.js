// Session Search - Handles view/edit mode switching for existing sessions
function sessionSearch() {
    return {
        filters: {
            title: '',
            description: '',
            status: {
                scheduled: false,
                completed: false,
                skipped: false,
                cancelled: false
            },
            activeStatus: 'all',
            completionStatus: 'all'
        },
        simpleSearch: '',
        expanded: false,
        saving: false,

        expand() {
            this.expanded = true;
        },

        collapse() {
            this.expanded = false;
        },

        applySimpleSearch() {
            console.log('Applying simple search:', this.simpleSearch);
            // TODO: Implement search logic
        },

        applyFilters() {
            console.log('Applying filters:', this.filters);
            // TODO: Implement filter logic
        },

        clearFilters() {
            this.filters.title = '';
            this.filters.description = '';
            this.filters.status.scheduled = false;
            this.filters.status.completed = false;
            this.filters.status.skipped = false;
            this.filters.status.cancelled = false;
            this.filters.activeStatus = 'all';
            this.filters.completionStatus = 'all';
        },

        hasActiveFilters() {
            return (
                this.filters.title ||
                this.filters.description ||
                Object.values(this.filters.status).some(Boolean) ||
                this.filters.activeStatus !== 'all' ||
                this.filters.completionStatus !== 'all'
            );
        },

        getActiveFilterCount() {
            let count = 0;

            if (this.filters.title) count++;
            if (this.filters.description) count++;
            Object.values(this.filters.status).forEach(value => {
                if (value) count++;
            });
            if (this.filters.activeStatus !== 'all') count++;
            if (this.filters.completionStatus !== 'all') count++;

            return count;
        }
    };
}
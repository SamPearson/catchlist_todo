// Task Search - Handles search and filtering
function taskSearch() {
    return {
        expanded: false,
        loading: false,
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
            activeStatus: 'all',         // 'active', 'all', 'inactive'
            completionStatus: 'incomplete' // 'incomplete', 'all', 'complete'
        },

        expand() {
            this.expanded = true;
        },

        collapse() {
            this.expanded = false;
        },

        init() {
        },

        // Build the query params object from current filter state
        buildParams(overrides = {}) {
            const params = {};

            const title = overrides.title ?? this.filters.title;
            const description = overrides.description ?? this.filters.description;

            if (title) params.title = title;
            if (description) params.description = description;

            // Status filter: if any checked, pass as comma-separated string
            const selectedStatuses = Object.entries(this.filters.status)
                .filter(([, v]) => v === true)
                .map(([k]) => k);
            if (selectedStatuses.length > 0) {
                params.status = selectedStatuses.join(',');
            }

            // Active filter
            if (this.filters.activeStatus === 'active') params.active = 'true';
            if (this.filters.activeStatus === 'inactive') params.active = 'false';

            // Completion filter
            if (this.filters.completionStatus === 'all') params.include_completed = 'true';
            if (this.filters.completionStatus === 'complete') {
                params.include_completed = 'true';
                params.completed = 'true';
            }

            return params;
        },

        async fetchAndDispatch(params) {
            this.loading = true;
            try {
                const tasks = await api.get('/api/tasks', params);
                this.$dispatch('tasks-search', tasks || []);
            } catch (err) {
                console.error('Error fetching tasks:', err);
                alert('Error searching tasks: ' + err.message);
            } finally {
                this.loading = false;
            }
        },

        updateFilters() {
            const params = this.buildParams();
            this.$dispatch('tasks-search', params);
        },

        async clearFilters() {
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

            // Re-fetch with cleared filters (back to default: incomplete tasks only)
            await this.fetchAndDispatch({});

            // Dispatch empty filters to ensure task list is reset
            this.$dispatch('tasks-search', {});
        },

        hasActiveFilters() {
            if (this.filters.title) return true;
            if (this.filters.description) return true;

            const hasStatusFilter = Object.values(this.filters.status).some(v => v === true);
            if (hasStatusFilter) return true;

            if (this.filters.activeStatus !== 'all') return true;
            if (this.filters.completionStatus !== 'incomplete') return true;

            return false;
        },

        getActiveFilterCount() {
            let count = 0;

            if (this.filters.title) count++;
            if (this.filters.description) count++;

            count += Object.values(this.filters.status).filter(v => v === true).length;

            if (this.filters.activeStatus !== 'all') count++;
            if (this.filters.completionStatus !== 'incomplete') count++;

            return count;
        },

        getFilterSummary() {
            const parts = [];

            if (this.filters.title) parts.push('Title contains: "' + this.filters.title + '"');
            if (this.filters.description) parts.push('Description contains: "' + this.filters.description + '"');

            const selectedStatuses = Object.entries(this.filters.status)
                .filter(([, v]) => v === true)
                .map(([k]) => k);
            if (selectedStatuses.length > 0) parts.push('Status: ' + selectedStatuses.join(', '));

            if (this.filters.activeStatus !== 'all') parts.push('Active: ' + this.filters.activeStatus);
            if (this.filters.completionStatus !== 'incomplete') parts.push('Completion: ' + this.filters.completionStatus);

            return parts.length > 0 ? parts.join('\n') : 'No filters active';
        }
    };
}
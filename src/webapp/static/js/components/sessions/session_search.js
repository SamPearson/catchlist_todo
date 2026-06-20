// Session Search - Handles search and filtering with API requests
function sessionSearch() {
    return {
        expanded: false,
        loading: false,
        filters: {
            status: {
                scheduled: false,
                completed: false,
                skipped: false,
                cancelled: false
            },
            tags: [],
            principles: [],
            tagInput: '',
            principleInput: ''
        },
        dateRange: {
            start: '',
            end: ''
        },

        init() {
            // Set default date range to today
            const today = new Date();
            const start = new Date(today);
            start.setHours(0, 0, 0, 0);
            const end = new Date(today);
            end.setHours(23, 59, 59, 999);

            this.dateRange.start = start.toISOString().slice(0, 16);
            this.dateRange.end = end.toISOString().slice(0, 16);
        },

        expand() {
            this.expanded = true;
        },

        collapse() {
            this.expanded = false;
        },

        addTag() {
            if (this.filters.tagInput.trim()) {
                this.filters.tags.push(this.filters.tagInput.trim());
                this.filters.tagInput = '';
            }
        },

        removeTag(index) {
            this.filters.tags.splice(index, 1);
        },

        addPrinciple() {
            if (this.filters.principleInput.trim()) {
                this.filters.principles.push(this.filters.principleInput.trim());
                this.filters.principleInput = '';
            }
        },

        removePrinciple(index) {
            this.filters.principles.splice(index, 1);
        },

        buildParams() {
            const params = {};

            // Add date range
            if (this.dateRange.start) {
                params.start = new Date(this.dateRange.start).toISOString();
            }
            if (this.dateRange.end) {
                params.end = new Date(this.dateRange.end).toISOString();
            }

            // Add status filters (repeated params for OR logic)
            const selectedStatuses = Object.entries(this.filters.status)
                .filter(([, v]) => v === true)
                .map(([k]) => k);
            selectedStatuses.forEach(status => {
                if (!params.status) {
                    params.status = [];
                }
                params.status.push(status);
            });

            // Add tags (repeated params for OR logic)
            if (this.filters.tags.length > 0) {
                params.tags = this.filters.tags;
            }

            // Add principles (repeated params for OR logic)
            if (this.filters.principles.length > 0) {
                params.principles = this.filters.principles;
            }

            return params;
        },

        async search() {
            this.loading = true;
            try {
                const params = this.buildParams();
                const sessions = await api.get('/api/sessions', params);
                this.$dispatch('sessions-search', { sessions: sessions || [] });
            } catch (err) {
                console.error('Error fetching sessions:', err);
                alert('Error searching sessions: ' + err.message);
            } finally {
                this.loading = false;
            }
        },

        async clearFilters() {
            this.filters = {
                status: {
                    scheduled: false,
                    completed: false,
                    skipped: false,
                    cancelled: false
                },
                tags: [],
                principles: [],
                tagInput: '',
                principleInput: ''
            };

            // Reset to today and fetch
            const today = new Date();
            const start = new Date(today);
            start.setHours(0, 0, 0, 0);
            const end = new Date(today);
            end.setHours(23, 59, 59, 999);

            this.dateRange.start = start.toISOString().slice(0, 16);
            this.dateRange.end = end.toISOString().slice(0, 16);

            await this.search();
        },

        hasActiveFilters() {
            return (
                Object.values(this.filters.status).some(v => v === true) ||
                this.filters.tags.length > 0 ||
                this.filters.principles.length > 0
            );
        },

        getActiveFilterCount() {
            let count = 0;
            count += Object.values(this.filters.status).filter(v => v === true).length;
            count += this.filters.tags.length;
            count += this.filters.principles.length;
            return count;
        }
    };
}
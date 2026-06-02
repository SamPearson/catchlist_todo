function reportDisplay(initialReport) {
    return {
        report: { ...initialReport },
        editing: false,
        saveNotification: false,
        showWindowed: false,

        // Draft state — populated when entering edit mode
        draft: {},

        // Commitment splitting
        get taskCommitments() {
            if (!this.report.commitments) return [];
            return this.report.commitments
                .filter(c => c.target_type === 'task')
                .map(c => c.target);
        },

        get sessionCommitments() {
            if (!this.report.commitments) return [];
            return this.report.commitments
                .filter(c => c.target_type === 'session')
                .map(c => c.target);
        },

        // Windowed day stubs for week reports
        get weekDayStubs() {
            if (this.report.report_type !== 'week') return [];
            // Derive Monday from the report's date field
            const [y, m, d] = this.report.date.split('-').map(Number);
            const monday = new Date(y, m - 1, d);
            return Array.from({ length: 7 }, (_, i) => {
                const day = new Date(monday);
                day.setDate(monday.getDate() + i);
                return day.toLocaleDateString('en-US', { weekday: 'long', month: 'short', day: 'numeric' });
            });
        },

        enterEdit() {
            this.draft = {
                plan:       this.report.plan       || '',
                reason:     this.report.reason     || '',
                pre_notes:  this.report.pre_notes  || '',
                post_notes: this.report.post_notes || '',
            };
            this.editing = true;
        },

        cancelEdit() {
            this.draft = {};
            this.editing = false;
        },

        saveEdit() {
            this.report.plan       = this.draft.plan;
            this.report.reason     = this.draft.reason;
            this.report.pre_notes  = this.draft.pre_notes;
            this.report.post_notes = this.draft.post_notes;
            this.editing = false;
            this.draft = {};
            this.saveNotification = true;
            setTimeout(() => { this.saveNotification = false; }, 3000);
        },

        // Stats helpers
        get statsByType() {
            if (!this.report.stats || !this.report.stats.by_type) return [];
            return Object.entries(this.report.stats.by_type).map(([type, count]) => ({ type, count }));
        },

        get statsByStatus() {
            if (!this.report.stats || !this.report.stats.by_status) return [];
            return Object.entries(this.report.stats.by_status).map(([status, count]) => ({ status, count }));
        },

        reportTypeBadgeClass() {
            const classes = {
                day:    'is-info',
                week:   'is-link',
                month:  'is-primary',
                season: 'is-success',
                year:   'is-warning',
            };
            return classes[this.report.report_type] || 'is-light';
        },
    };
}
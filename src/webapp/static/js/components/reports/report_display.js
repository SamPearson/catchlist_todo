/**
 * Page-level orchestrator
 * Manages report state, API calls, and event coordination
 * Dispatches events to notify the display component of changes
 */
function reportPageOrchestrator() {
    return {
        report: INITIAL_REPORT,
        loading: false,
        error: null,

    async loadReport(timeframe) {
        console.log('[Orchestrator] loadReport called with timeframe:', timeframe);
        this.loading = true;
        this.error = null;

        try {
            let endpoint;

            // Construct endpoint based on timeframe type
            if (timeframe.type === 'day' || timeframe.type === 'week') {
                endpoint = `/api/reports/${timeframe.type}/${timeframe.date}?full=true&include_commitments=False`;
            } else if (timeframe.type === 'month') {
                endpoint = `/api/reports/${timeframe.type}/${timeframe.year}-${String(timeframe.month).padStart(2, '0')}-01?full=true&include_commitments=False`;
            } else if (timeframe.type === 'season') {
                // Use first day of season: Jan for winter, Apr for spring, Jul for summer, Oct for fall
                const seasonMonths = { winter: 1, spring: 4, summer: 7, fall: 10 };
                const month = seasonMonths[timeframe.season];
                endpoint = `/api/reports/${timeframe.type}/${timeframe.year}-${String(month).padStart(2, '0')}-01?full=true&include_commitments=False`;
            } else if (timeframe.type === 'year') {
                endpoint = `/api/reports/${timeframe.type}/${timeframe.year}-01-01?full=true&include_commitments=False`;
            }

            console.log('[Orchestrator] Fetching from endpoint:', endpoint);
            const report = await api.get(endpoint);
            console.log('[Orchestrator] Received report:', report);
            if (report) {
                this.report = report;
                console.log('[Orchestrator] Report updated, dispatching load-report event');
                window.dispatchEvent(new CustomEvent('load-report', { detail: report }));
                console.log('[Orchestrator] Event dispatched');
            } else {
                this.error = 'Report not found';
                console.log('[Orchestrator] Report not found');
            }
        } catch (err) {
            this.error = err.message || 'Failed to load report';
            console.error('[Orchestrator] Error loading report:', err);
        } finally {
            this.loading = false;
        }
    },

        async saveReport(updates) {
            console.log('[Orchestrator] saveReport called with updates:', updates);
            this.error = null;

            try {
                const endpoint = `/api/reports/${this.report.id}?full=true`;
                console.log('[Orchestrator] Saving to endpoint:', endpoint);
                const updated = await api.put(endpoint, updates);
                console.log('[Orchestrator] Received updated report:', updated);
                if (updated) {
                    this.report = updated;
                    console.log('[Orchestrator] Report updated, dispatching load-report event');
                    // Dispatch to window so display component can hear it
                    window.dispatchEvent(new CustomEvent('load-report', { detail: updated }));
                    console.log('[Orchestrator] Event dispatched');
                } else {
                    this.error = 'Failed to save report';
                    console.log('[Orchestrator] Save returned falsy value');
                }
            } catch (err) {
                this.error = err.message || 'Failed to save report';
                console.error('[Orchestrator] Error saving report:', err);
            }
        },
    };
}


/**
 * Display component
 * Pure presentation layer — receives report data and renders it
 * Syncs when orchestrator dispatches load-report event
 */
function reportDisplay() {
    return {
        report: { ...INITIAL_REPORT },
        editing: false,
        saveNotification: false,
        showWindowed: false,
        draft: {},

        init() {
            console.log('[Display] Component initialized, report:', this.report);
            window.addEventListener('load-report', (event) => {
                console.log('[Display] load-report event received:', event.detail);
                this.syncReport(event.detail);
            });
        },

        // Sync report data when orchestrator notifies
        syncReport(newReport) {
            console.log('[Display] syncReport called with:', newReport);
            this.report = { ...newReport };
            console.log('[Display] report updated to:', this.report);
        },

        // Format ISO datetime string safely
        formatDate(dateStr) {
            if (!dateStr) return '';
            try {
                return new Date(dateStr).toLocaleDateString();
            } catch {
                return 'Invalid Date';
            }
        },

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
            // Derive Monday from the report's label field
            const [y, m, d] = this.report.label.split('-').map(Number);
            const monday = new Date(y, m - 1, d);
            return Array.from({ length: 7 }, (_, i) => {
                const day = new Date(monday);
                day.setDate(monday.getDate() + i);
                return day.toLocaleDateString('en-US', { weekday: 'long', month: 'short', day: 'numeric' });
            });
        },

        enterEdit() {
            console.log('[Display] enterEdit called');
            this.draft = {
                plan:       this.report.plan       || '',
                reason:     this.report.reason     || '',
                pre_notes:  this.report.pre_notes  || '',
                post_notes: this.report.post_notes || '',
            };
            this.editing = true;
        },

        cancelEdit() {
            console.log('[Display] cancelEdit called');
            this.draft = {};
            this.editing = false;
        },

        saveEdit() {
            console.log('[Display] saveEdit called with draft:', this.draft);
            const updates = {
                plan:       this.draft.plan,
                reason:     this.draft.reason,
                pre_notes:  this.draft.pre_notes,
                post_notes: this.draft.post_notes,
            };
            this.$dispatch('report-save', updates);
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
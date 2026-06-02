function reportSelector() {
    return {
        reportType: 'day',
        reportTypes: ['day', 'week', 'month', 'season', 'year'],

        // Per-type selection state
        day: {
            date: new Date().toISOString().slice(0, 10), // YYYY-MM-DD
        },
        week: {
            date: new Date().toISOString().slice(0, 10), // Any date within the desired week
        },
        month: {
            year: new Date().getFullYear(),
            month: new Date().getMonth() + 1, // 1-12
        },
        season: {
            year: new Date().getFullYear(),
            season: _currentSeason(),
        },
        year: {
            year: new Date().getFullYear(),
        },

        // --- Helpers ---


        _parseLocalDate(dateStr) {
            // Parse YYYY-MM-DD without timezone shift
            const [y, m, d] = dateStr.split('-').map(Number);
            return new Date(y, m - 1, d);
        },

        // --- Labels ---

        get selectionLabel() {
            switch (this.reportType) {
                case 'day':
                    return this._formatDay(this.day.date);
                case 'week':
                    return this._formatWeek(this.week.date);
                case 'month':
                    return this._formatMonth(this.month.year, this.month.month);
                case 'season':
                    return this._formatSeason(this.season.year, this.season.season);
                case 'year':
                    return String(this.year.year);
            }
        },

        _formatDay(dateStr) {
            const d = this._parseLocalDate(dateStr);
            return d.toLocaleDateString('en-US', { weekday: 'long', year: 'numeric', month: 'long', day: 'numeric' });
        },

        _formatWeek(dateStr) {
            const d = this._parseLocalDate(dateStr);
            const monday = this._weekStart(d);
            const sunday = new Date(monday);
            sunday.setDate(monday.getDate() + 6);
            const opts = { month: 'short', day: 'numeric' };
            return `Week of ${monday.toLocaleDateString('en-US', opts)} – ${sunday.toLocaleDateString('en-US', opts)}, ${sunday.getFullYear()}`;
        },

        _formatMonth(year, month) {
            const d = new Date(year, month - 1, 1);
            return d.toLocaleDateString('en-US', { month: 'long', year: 'numeric' });
        },

        _formatSeason(year, season) {
            return `${season.charAt(0).toUpperCase() + season.slice(1)} ${year}`;
        },

        _weekStart(date) {
            // Returns the Monday of the week containing `date`
            const d = new Date(date);
            const day = d.getDay(); // 0=Sun, 1=Mon...
            const diff = (day === 0) ? -6 : 1 - day;
            d.setDate(d.getDate() + diff);
            return d;
        },

        // --- Navigation ---

        prev() {
            switch (this.reportType) {
                case 'day': {
                    const d = this._parseLocalDate(this.day.date);
                    d.setDate(d.getDate() - 1);
                    this.day.date = d.toISOString().slice(0, 10);
                    break;
                }
                case 'week': {
                    const d = this._parseLocalDate(this.week.date);
                    d.setDate(d.getDate() - 7);
                    this.week.date = d.toISOString().slice(0, 10);
                    break;
                }
                case 'month': {
                    this.month.month--;
                    if (this.month.month < 1) { this.month.month = 12; this.month.year--; }
                    break;
                }
                case 'season': {
                    const seasons = ['winter', 'spring', 'summer', 'fall'];
                    const idx = seasons.indexOf(this.season.season);
                    if (idx === 0) { this.season.season = 'fall'; this.season.year--; }
                    else { this.season.season = seasons[idx - 1]; }
                    break;
                }
                case 'year': {
                    this.year.year--;
                    break;
                }
            }
        },

        next() {
            switch (this.reportType) {
                case 'day': {
                    const d = this._parseLocalDate(this.day.date);
                    d.setDate(d.getDate() + 1);
                    this.day.date = d.toISOString().slice(0, 10);
                    break;
                }
                case 'week': {
                    const d = this._parseLocalDate(this.week.date);
                    d.setDate(d.getDate() + 7);
                    this.week.date = d.toISOString().slice(0, 10);
                    break;
                }
                case 'month': {
                    this.month.month++;
                    if (this.month.month > 12) { this.month.month = 1; this.month.year++; }
                    break;
                }
                case 'season': {
                    const seasons = ['winter', 'spring', 'summer', 'fall'];
                    const idx = seasons.indexOf(this.season.season);
                    if (idx === seasons.length - 1) { this.season.season = 'winter'; this.season.year++; }
                    else { this.season.season = seasons[idx + 1]; }
                    break;
                }
                case 'year': {
                    this.year.year++;
                    break;
                }
            }
        },

        // --- Resolved timeframe payload ---
        // This is what gets dispatched when the user clicks "Load Report".
        // It represents a normalised, type-agnostic description of the selection
        // that the display component (and eventually the API call) will consume.

        get resolvedTimeframe() {
            switch (this.reportType) {
                case 'day':
                    return { type: 'day', date: this.day.date, label: this.selectionLabel };
                case 'week': {
                    const monday = this._weekStart(this._parseLocalDate(this.week.date));
                    return {
                        type: 'week',
                        date: monday.toISOString().slice(0, 10), // canonical: Monday
                        label: this.selectionLabel,
                    };
                }
                case 'month':
                    return { type: 'month', year: this.month.year, month: this.month.month, label: this.selectionLabel };
                case 'season':
                    return { type: 'season', year: this.season.year, season: this.season.season, label: this.selectionLabel };
                case 'year':
                    return { type: 'year', year: this.year.year, label: this.selectionLabel };
            }
        },

        loadReport() {
            this.$dispatch('report-selected', this.resolvedTimeframe);
        },
    };
}

function _currentSeason() {
    const month = new Date().getMonth() + 1;
    if (month >= 3 && month <= 5) return 'spring';
    if (month >= 6 && month <= 8) return 'summer';
    if (month >= 9 && month <= 11) return 'fall';
    return 'winter';
}
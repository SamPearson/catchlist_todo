function projectSearch() {
  return {
    expanded: false,
    loading: false,
    filters: {
      title: '',
      description: '',
      status: { open: false, waiting: false, deferred: false, declined: false, stale: false },
      activity: 'all',
      completion: 'incomplete'
    },

    expand() {
      this.expanded = true;
    },

    collapse() {
      this.expanded = false;
      this.updateFilters();
    },

    clearFilters() {
      this.filters = {
        title: '',
        description: '',
        status: { open: false, waiting: false, deferred: false, declined: false, stale: false },
        activity: 'all',
        completion: 'incomplete'
      };
      this.updateFilters();
    },

    buildParams(overrides = {}) {
      const params = {};
      if (this.filters.title) params.title = this.filters.title;
      if (this.filters.description) params.description = this.filters.description;
      const statuses = Object.keys(this.filters.status).filter(s => this.filters.status[s]);
      if (statuses.length > 0) params.status = statuses.join(',');
      if (this.filters.activity !== 'all') {
        params.active = this.filters.activity === 'active' ? 'true' : 'false';
      }
      if (this.filters.completion !== 'all') {
        params.completed = this.filters.completion === 'complete' ? 'true' : 'false';
      }
      return { ...params, ...overrides };
    },

    updateFilters() {
      const params = this.buildParams();
      window.dispatchEvent(new CustomEvent('projects-search', { detail: params }));
    },

    hasActiveFilters() {
      return this.getActiveFilterCount() > 0;
    },

    getActiveFilterCount() {
      let count = 0;
      if (this.filters.title) count++;
      if (this.filters.description) count++;
      count += Object.keys(this.filters.status).filter(s => this.filters.status[s]).length;
      if (this.filters.activity !== 'all') count++;
      if (this.filters.completion !== 'incomplete') count++;
      return count;
    },

    getFilterSummary() {
      const parts = [];
      if (this.filters.title) parts.push(`Title: "${this.filters.title}"`);
      if (this.filters.description) parts.push(`Description: "${this.filters.description}"`);
      const statuses = Object.keys(this.filters.status).filter(s => this.filters.status[s]);
      if (statuses.length) parts.push(`Status: ${statuses.join(', ')}`);
      if (this.filters.activity !== 'all') parts.push(`Activity: ${this.filters.activity}`);
      if (this.filters.completion !== 'incomplete') parts.push(`Completion: ${this.filters.completion}`);
      return parts.join(' · ');
    }
  };
}
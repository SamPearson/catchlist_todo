function projectList(initialProjects) {
  return {
    initialProjects: initialProjects,
    projects: initialProjects,
    error: null,
    eventListenersAdded: false,

    init() {
      if (this.eventListenersAdded) return;
      window.addEventListener('project-created', (event) => this.onProjectCreated(event));
      window.addEventListener('project-updated', (event) => this.onProjectUpdated(event));
      window.addEventListener('project-deleted', (event) => this.onProjectDeleted(event));
      window.addEventListener('projects-search', (event) => this.onProjectsSearch(event));
      this.eventListenersAdded = true;
    },

    onProjectCreated(event) {
      const project = event.detail.project;
      this.projects = [...this.projects, project];
      this.initialProjects = [...this.initialProjects, project];
    },

    onProjectUpdated(event) {
      const updated = event.detail.project;
      if (!updated) return;
      this.projects = this.projects.map(p => p.id === updated.id ? updated : p);
      this.initialProjects = this.initialProjects.map(p => p.id === updated.id ? updated : p);
    },

    onProjectDeleted(event) {
      const projectId = event.detail.projectId;
      this.projects = this.projects.filter(p => p.id !== projectId);
      this.initialProjects = this.initialProjects.filter(p => p.id !== projectId);
    },

    onProjectsSearch(event) {
      const params = event.detail || {};
      let results = [...this.initialProjects];

      if (params.title) {
        const title = params.title.toLowerCase();
        results = results.filter(p => (p.title || '').toLowerCase().includes(title));
      }

      if (params.description) {
        const desc = params.description.toLowerCase();
        results = results.filter(p => (p.description || '').toLowerCase().includes(desc));
      }

      if (params.status) {
        const selectedStatuses = params.status.split(',');
        results = results.filter(p => selectedStatuses.includes(p.status));
      }

      if (params.activity && params.activity !== 'all') {
        const wantActive = params.activity === 'active';
        results = results.filter(p => p.active === wantActive);
      }

      if (params.completion && params.completion !== 'all') {
        const wantComplete = params.completion === 'complete';
        results = results.filter(p => p.completed === wantComplete);
      }

      this.projects = results;
      this.error = null;
    }
  };
}
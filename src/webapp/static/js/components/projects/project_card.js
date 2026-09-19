function projectCard(initialProject) {
  return {
    project: initialProject,
    mode: 'view',
    expanded: false,
    formData: {},
    errors: {},
    saving: false,
    error: null,

    subtasks: [],
    subtasksLoaded: false,
    loadingSubtasks: false,
    subtasksError: null,
    quickTitle: '',
    savingSubtask: false,
    attachMode: false,
    attaching: false,
    standaloneTasks: [],
    attachTaskId: '',

    showActivateForm: false,

    edit() {
      this.mode = 'edit';
      this.formData = {
        title: this.project.title,
        description: this.project.description,
        win_condition: this.project.win_condition,
        reason: this.project.reason,
        next_step: this.project.next_step,
        status: this.project.status
      };
      this.errors = {};
      this.error = null;
    },

    toggleExpand() {
      this.expanded = !this.expanded;
      if (this.expanded && !this.subtasksLoaded) {
        this.loadSubtasks();
      }
    },

    cancelEdit() {
      this.mode = 'view';
      this.errors = {};
      this.error = null;
    },

    validate() {
      this.errors = {};
      if (!this.formData.title || !this.formData.title.trim()) {
        this.errors.title = 'Project title is required.';
      } else if (this.formData.title.length > 200) {
        this.errors.title = 'Project title cannot exceed 200 characters.';
      }
      return Object.keys(this.errors).length === 0;
    },

    async save() {
      if (!this.validate()) return;
      this.saving = true;
      this.error = null;
      try {
        const payload = {
          title: this.formData.title,
          description: this.formData.description,
          win_condition: this.formData.win_condition,
          reason: this.formData.reason,
          next_step: this.formData.next_step
        };
        let updated = await api.put(`/api/projects/${this.project.id}`, payload);
        if (this.formData.status !== this.project.status) {
          updated = await api.patch(`/api/projects/${this.project.id}/status`, { status: this.formData.status });
        }
        this.project = updated;
        this.mode = 'view';
        this.$dispatch('project-updated', updated);
      } catch (err) {
        console.error('Error saving project:', err);
        this.error = err.message || 'Error saving project.';
      } finally {
        this.saving = false;
      }
    },

    requestActivate() {
      const missing = [];
      if (!this.project.win_condition) missing.push('win condition');
      if (!this.project.reason) missing.push('reason');
      if (!this.project.next_step) missing.push('next step');
      if (missing.length > 0) {
        this.showActivateForm = true;
        this.formData = {
          win_condition: this.project.win_condition || '',
          reason: this.project.reason || '',
          next_step: this.project.next_step || ''
        };
        return;
      }
      this.activate();
    },

    cancelActivate() {
      this.showActivateForm = false;
    },

    async saveAndActivate() {
      if (!this.formData.win_condition || !this.formData.reason || !this.formData.next_step) {
        this.error = 'Win condition, reason, and next step are all required to activate.';
        return;
      }
      this.saving = true;
      try {
        let updated = await api.put(`/api/projects/${this.project.id}`, {
          win_condition: this.formData.win_condition,
          reason: this.formData.reason,
          next_step: this.formData.next_step
        });
        updated = await api.patch(`/api/projects/${this.project.id}/activate`, {});
        this.project = updated;
        this.showActivateForm = false;
        this.mode = 'view';
        this.$dispatch('project-updated', updated);
      } catch (err) {
        console.error('Error activating project:', err);
        this.error = err.message || 'Error activating project.';
      } finally {
        this.saving = false;
      }
    },

    async activate() {
      this.saving = true;
      try {
        const updated = await api.patch(`/api/projects/${this.project.id}/activate`, {});
        this.project = updated;
        this.mode = 'view';
        this.$dispatch('project-updated', updated);
      } catch (err) {
        console.error('Error activating project:', err);
        alert(err.message || 'Error activating project.');
      } finally {
        this.saving = false;
      }
    },

    async completeProject() {
      if (!confirm('Complete this project?')) return;
      this.saving = true;
      try {
        const updated = await api.patch(`/api/projects/${this.project.id}/complete`, {});
        this.project = updated;
        this.$dispatch('project-updated', updated);
      } catch (err) {
        console.error('Error completing project:', err);
        alert(err.message || 'Error completing project.');
      } finally {
        this.saving = false;
      }
    },

    async uncompleteProject() {
      this.saving = true;
      try {
        const updated = await api.patch(`/api/projects/${this.project.id}/uncomplete`, {});
        this.project = updated;
        this.$dispatch('project-updated', updated);
      } catch (err) {
        console.error('Error uncompleting project:', err);
        alert(err.message || 'Error uncompleting project.');
      } finally {
        this.saving = false;
      }
    },

    async deleteProject() {
      if (!confirm('Delete this project? All subtasks will be deleted. This cannot be undone.')) return;
      this.saving = true;
      try {
        await api.delete(`/api/projects/${this.project.id}`);
        this.$dispatch('project-deleted', { projectId: this.project.id });
      } catch (err) {
        console.error('Error deleting project:', err);
        this.error = err.message || 'Error deleting project.';
      } finally {
        this.saving = false;
      }
    },

    async loadSubtasks() {
      this.loadingSubtasks = true;
      this.subtasksError = null;
      try {
        this.subtasks = await api.get(`/api/projects/${this.project.id}/tasks?include_completed=true`) || [];
        this.subtasksLoaded = true;
      } catch (err) {
        console.error('Error loading subtasks:', err);
        this.subtasksError = err.message || 'Error loading subtasks.';
      } finally {
        this.loadingSubtasks = false;
      }
    },

    async quickCreateSubtask() {
      if (!this.quickTitle || !this.quickTitle.trim()) return;
      this.savingSubtask = true;
      try {
        const task = await api.post(`/api/projects/${this.project.id}/tasks`, { title: this.quickTitle.trim() });
        this.subtasks = [...this.subtasks, task];
        this.quickTitle = '';
      } catch (err) {
        console.error('Error creating subtask:', err);
        this.subtasksError = err.message || 'Error creating subtask.';
      } finally {
        this.savingSubtask = false;
      }
    },

    async completeSubtask(sub) {
      try {
        const updated = await api.patch(`/api/tasks/${sub.id}/complete?toggle=true`);
        this.subtasks = this.subtasks.map(t => t.id === updated.id ? updated : t);
      } catch (err) {
        console.error('Error completing subtask:', err);
        this.subtasksError = err.message || 'Error completing subtask.';
      }
    },

    async detachSubtask(sub) {
      if (!confirm(`Detach "${sub.title}" from this project?`)) return;
      try {
        await api.patch(`/api/tasks/${sub.id}/detach`);
        this.subtasks = this.subtasks.filter(t => t.id !== sub.id);
      } catch (err) {
        console.error('Error detaching subtask:', err);
        this.subtasksError = err.message || 'Error detaching subtask.';
      }
    },

    async toggleAttach() {
      this.attachMode = !this.attachMode;
      if (this.attachMode && this.standaloneTasks.length === 0) {
        this.loadingSubtasks = true;
        try {
          const tasks = await api.get('/api/tasks?include_completed=true') || [];
          this.standaloneTasks = tasks.filter(t => !t.project_id);
        } catch (err) {
          console.error('Error loading standalone tasks:', err);
          this.subtasksError = err.message || 'Error loading standalone tasks.';
        } finally {
          this.loadingSubtasks = false;
        }
      }
    },

    async attachSubtask() {
      if (!this.attachTaskId) return;
      this.attaching = true;
      try {
        const task = await api.patch(`/api/tasks/${this.attachTaskId}/attach/${this.project.id}`);
        this.subtasks = [...this.subtasks, task];
        this.standaloneTasks = this.standaloneTasks.filter(t => t.id !== task.id);
        this.attachTaskId = '';
        this.attachMode = false;
      } catch (err) {
        console.error('Error attaching subtask:', err);
        this.subtasksError = err.message || 'Error attaching subtask.';
      } finally {
        this.attaching = false;
      }
    },

    getStatusColor() {
      const map = {
        'open': 'status-open',
        'waiting': 'status-waiting',
        'deferred': 'status-deferred',
        'declined': 'status-declined',
        'stale': 'status-stale'
      };
      return map[this.project.status] || 'status-open';
    },

    getStatusTagClass() {
      const map = {
        'open': 'tag-info',
        'waiting': 'tag-warning',
        'deferred': 'tag-grey',
        'declined': 'tag-danger',
        'stale': 'tag-grey'
      };
      return map[this.project.status] || 'tag-info';
    },

    formatDate(value) {
      if (!value) return '-';
      const d = new Date(value);
      if (isNaN(d.getTime())) return value;
      return d.toLocaleString('en-US');
    }
  };
}
function projectCreate() {
  return {
    formData: {
      title: '',
      description: '',
      win_condition: '',
      reason: '',
      next_step: '',
      status: 'open',
      active: true
    },
    errors: {},
    saving: false,
    expanded: false,

    toggleExpand() {
      this.expanded = !this.expanded;
    },

    validate() {
      this.errors = {};
      if (!this.formData.title || !this.formData.title.trim()) {
        this.errors.title = 'Project title is required.';
      } else if (this.formData.title.length > 200) {
        this.errors.title = 'Project title cannot exceed 200 characters.';
      }
      if (this.formData.active) {
        if (!this.formData.win_condition) {
          this.errors.win_condition = 'Required when starting active.';
        }
        if (!this.formData.reason) {
          this.errors.reason = 'Required when starting active.';
        }
        if (!this.formData.next_step) {
          this.errors.next_step = 'Required when starting active.';
        }
      }
      return Object.keys(this.errors).length === 0;
    },

    async create() {
      if (!this.validate()) return;
      this.saving = true;
      try {
        const payload = {
          title: this.formData.title,
          description: this.formData.description,
          win_condition: this.formData.win_condition,
          reason: this.formData.reason,
          next_step: this.formData.next_step,
          status: this.formData.status,
          active: this.formData.active
        };
        if (!this.formData.active) {
          delete payload.active;
        }
        const newProject = await api.post('/api/projects', payload);
        console.log('New project created:', newProject);
        this.$dispatch('project-created', { project: newProject });
        this.formData = {
          title: '',
          description: '',
          win_condition: '',
          reason: '',
          next_step: '',
          status: 'open',
          active: true
        };
        this.expanded = false;
      } catch (err) {
        console.error('Error creating project:', err);
        this.errors.general = err.message || 'Error creating project.';
      } finally {
        this.saving = false;
      }
    },

    cancel() {
      this.formData = {
        title: '',
        description: '',
        win_condition: '',
        reason: '',
        next_step: '',
        status: 'open',
        active: true
      };
      this.errors = {};
    }
  };
}
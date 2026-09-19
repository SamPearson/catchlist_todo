function routineCreate() {
  return {
    formData: {
      title: '',
      description: '',
      start_time: '',
      end_time: '',
      calendar_id: '',
      active: true
    },
    rrule: RruleBuilder.empty(),
    dayOptions: RruleBuilder.DAY_OPTIONS,
    calendars: INITIAL_CALENDARS || [],
    errors: {},
    saving: false,
    expanded: false,

    toggleExpand() {
      this.expanded = !this.expanded;
    },

    rrulePreview() {
      return RruleBuilder.describe(this.rrule);
    },

    validate() {
      this.errors = {};
      if (!this.formData.title || !this.formData.title.trim()) {
        this.errors.title = 'Routine title is required.';
      } else if (this.formData.title.length > 200) {
        this.errors.title = 'Routine title cannot exceed 200 characters.';
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
          rrule: RruleBuilder.build(this.rrule),
          start_time: this.formData.start_time || null,
          end_time: this.formData.end_time || null,
          active: this.formData.active
        };
        if (this.formData.calendar_id) {
          payload.calendar_id = this.formData.calendar_id;
        }
        const newRoutine = await api.post('/api/routines', payload);
        console.log('New routine created:', newRoutine);
        this.$dispatch('routine-created', { routine: newRoutine });
        this.formData = {
          title: '',
          description: '',
          start_time: '',
          end_time: '',
          calendar_id: '',
          active: true
        };
        this.rrule = RruleBuilder.empty();
        this.expanded = false;
      } catch (err) {
        console.error('Error creating routine:', err);
        this.errors.general = err.message || 'Error creating routine.';
      } finally {
        this.saving = false;
      }
    },

    cancel() {
      this.formData = {
        title: '',
        description: '',
        start_time: '',
        end_time: '',
        calendar_id: '',
        active: true
      };
      this.rrule = RruleBuilder.empty();
      this.errors = {};
    }
  };
}
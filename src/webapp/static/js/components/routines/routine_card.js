function routineCard(initialRoutine) {
  return {
    routine: initialRoutine,
    mode: 'view',
    expanded: false,
    formData: {},
    rrule: RruleBuilder.empty(),
    dayOptions: RruleBuilder.DAY_OPTIONS,
    calendars: typeof INITIAL_CALENDARS !== 'undefined' ? INITIAL_CALENDARS : [],
    errors: {},
    saving: false,
    showDeleteModal: false,

    generateOpen: false,
    genStartDate: '',
    genEndDate: '',
    inheritTags: true,
    inheritPrinciples: true,
    generating: false,
    genMessage: '',
    genError: '',

    clearFutureOpen: false,
    clearPastOpen: false,
    clearingFuture: false,
    clearingPast: false,
    clearMessage: '',
    clearError: '',

    today() {
      return new Date().toISOString().slice(0, 10);
    },

    cssColor(value) {
      if (!value) return null;
      return value.startsWith('#') ? value : '#' + value;
    },

    calendarName() {
      const cal = this.calendars.find(c => String(c.id) === String(this.routine.calendar_id));
      return cal ? cal.name : (this.routine.calendar_name || 'No calendar');
    },

    calendarColor() {
      const cal = this.calendars.find(c => String(c.id) === String(this.routine.calendar_id));
      return (cal && cal.color) ? this.cssColor(cal.color) : this.cssColor(this.routine.calendar_color);
    },

    hasRrule() {
      return !!(this.routine.rrule);
    },

    rruleSummary() {
      return this.routine.rrule ? RruleBuilder.describe(RruleBuilder.parse(this.routine.rrule)) : 'Does not repeat';
    },

    formatTime(value) {
      if (!value) return '—';
      return value;
    },

    formatDate(value) {
      if (!value) return '—';
      return new Date(value).toLocaleString('en-US');
    },

    toggleExpand() {
      this.expanded = !this.expanded;
    },

    edit() {
      this.formData = {
        title: this.routine.title || '',
        description: this.routine.description || '',
        start_time: this.routine.start_time || '',
        end_time: this.routine.end_time || '',
        active: !!this.routine.active,
        calendar_id: this.routine.calendar_id ? String(this.routine.calendar_id) : '',
        cascade_future: false,
        cascade_past: false
      };
      this.rrule = RruleBuilder.parse(this.routine.rrule);
      this.errors = {};
      this.mode = 'edit';
    },

    cancelEdit() {
      this.mode = 'view';
      this.errors = {};
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

    async save() {
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
        const query = `cascade_future=${this.formData.cascade_future}&cascade_past=${this.formData.cascade_past}`;
        const updated = await api.patch(`/api/routines/${this.routine.id}?${query}`, payload);
        this.routine = updated;
        this.mode = 'view';
        this.$dispatch('routine-updated', { routine: updated });
      } catch (err) {
        console.error('Error updating routine:', err);
        this.errors.general = err.message || 'Error updating routine.';
      } finally {
        this.saving = false;
      }
    },

    async activate() {
      try {
        const updated = await api.patch(`/api/routines/${this.routine.id}`, { active: true });
        this.routine = updated;
        this.$dispatch('routine-updated', { routine: updated });
      } catch (err) {
        console.error('Error activating routine:', err);
        alert(err.message || 'Error activating routine.');
      }
    },

    async deactivate() {
      try {
        const updated = await api.patch(`/api/routines/${this.routine.id}`, { active: false });
        this.routine = updated;
        this.$dispatch('routine-updated', { routine: updated });
      } catch (err) {
        console.error('Error deactivating routine:', err);
        alert(err.message || 'Error deactivating routine.');
      }
    },

    async deleteRoutine() {
      try {
        await api.delete(`/api/routines/${this.routine.id}`);
        this.$dispatch('routine-deleted', { routineId: this.routine.id });
      } catch (err) {
        console.error('Error deleting routine:', err);
        alert(err.message || 'Error deleting routine.');
      }
    },

    async generateSessions() {
      if (!this.genStartDate || !this.genEndDate) {
        this.genError = 'Both a start date and end date are required.';
        return;
      }
      if (this.genStartDate > this.genEndDate) {
        this.genError = 'Start date must not be after end date.';
        return;
      }
      this.generating = true;
      this.genError = '';
      this.genMessage = '';
      try {
        const payload = {
          start_date: this.genStartDate,
          end_date: this.genEndDate,
          inherit_tags: this.inheritTags,
          inherit_principles: this.inheritPrinciples
        };
        const sessions = await api.post(`/api/routines/${this.routine.id}/sessions/generate`, payload);
        this.genMessage = `Generated ${Array.isArray(sessions) ? sessions.length : 0} session(s).`;
      } catch (err) {
        console.error('Error generating sessions:', err);
        this.genError = err.message || 'Error generating sessions.';
      } finally {
        this.generating = false;
      }
    },

    async clearFutureSessions() {
      this.clearingFuture = true;
      this.clearError = '';
      this.clearMessage = '';
      try {
        const result = await api.delete(`/api/routines/${this.routine.id}/sessions/future`);
        this.clearMessage = result && result.message ? result.message : 'Future sessions cleared.';
      } catch (err) {
        console.error('Error clearing future sessions:', err);
        this.clearError = err.message || 'Error clearing future sessions.';
      } finally {
        this.clearingFuture = false;
        this.clearFutureOpen = false;
      }
    },

    async clearPastSessions() {
      this.clearingPast = true;
      this.clearError = '';
      this.clearMessage = '';
      try {
        const result = await api.delete(`/api/routines/${this.routine.id}/sessions/past`);
        this.clearMessage = result && result.message ? result.message : 'Past sessions cleared.';
      } catch (err) {
        console.error('Error clearing past sessions:', err);
        this.clearError = err.message || 'Error clearing past sessions.';
      } finally {
        this.clearingPast = false;
        this.clearPastOpen = false;
      }
    }
  };
}
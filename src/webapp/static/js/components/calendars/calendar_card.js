function calendarCard(initialCalendar) {
  return {
    calendar: initialCalendar,
    mode: 'view',
    expanded: false,
    formData: {
      name: '',
      color: '#767676',
    },
    errors: {},
    saving: false,
    actionModal: {
      open: false,
      type: 'activate',
      cascade: true,
      saving: false,
      title: '',
      message: '',
      confirmLabel: '',
    },

    toggleExpand() {
      this.expanded = !this.expanded;
    },

    edit() {
      this.formData = {
        name: this.calendar.name || '',
        color: this.calendar.color && this.calendar.color.startsWith('#')
          ? this.calendar.color
          : `#${this.calendar.color || '767676'}`,
      };
      this.errors = {};
      this.mode = 'edit';
    },

    cancelEdit() {
      this.mode = 'view';
      this.errors = {};
    },

    validate() {
      this.errors = {};
      if (!this.formData.name || !this.formData.name.trim()) {
        this.errors.name = 'Calendar name is required.';
      } else if (this.formData.name.trim().length > 200) {
        this.errors.name = 'Calendar name cannot exceed 200 characters.';
      }
      if (!/^#[0-9A-Fa-f]{6}$/.test(this.formData.color)) {
        this.errors.color = 'Color must be in hex format (#RRGGBB).';
      }
      return Object.keys(this.errors).length === 0;
    },

    async save() {
      if (!this.validate()) return;
      this.saving = true;
      this.errors.general = '';
      const payload = {
        name: this.formData.name.trim(),
        color: this.formData.color,
      };
      try {
        const updated = await api.patch(`/api/calendars/${this.calendar.id}`, payload);
        this.calendar = updated;
        this.$dispatch('calendar-updated', updated);
        this.mode = 'view';
      } catch (err) {
        this.errors.general = err.message;
      } finally {
        this.saving = false;
      }
    },

    showActionModal(type) {
      const name = this.calendar.name || `Calendar #${this.calendar.id}`;
      if (type === 'activate') {
        this.actionModal = {
          open: true,
          type,
          cascade: true,
          saving: false,
          title: 'Activate Calendar',
          message: `Activate "${name}"?`,
          confirmLabel: 'Activate',
        };
      } else if (type === 'deactivate') {
        this.actionModal = {
          open: true,
          type,
          cascade: true,
          saving: false,
          title: 'Deactivate Calendar',
          message: `Deactivate "${name}"?`,
          confirmLabel: 'Deactivate',
        };
      } else {
        this.actionModal = {
          open: true,
          type: 'delete',
          cascade: true,
          saving: false,
          title: 'Delete Calendar',
          message: `Delete "${name}"?`,
          confirmLabel: 'Delete',
        };
      }
    },

    closeActionModal() {
      this.actionModal.open = false;
      this.actionModal.saving = false;
    },

    async confirmAction() {
      const { type, cascade } = this.actionModal;
      this.actionModal.saving = true;
      try {
        if (type === 'activate') {
          const updated = await api.patch(`/api/calendars/${this.calendar.id}/activate?cascade=${cascade}`, {});
          this.calendar = updated;
          this.$dispatch('calendar-updated', updated);
        } else if (type === 'deactivate') {
          const updated = await api.patch(`/api/calendars/${this.calendar.id}/deactivate?cascade=${cascade}`, {});
          this.calendar = updated;
          this.$dispatch('calendar-updated', updated);
        } else {
          await api.delete(`/api/calendars/${this.calendar.id}`);
          this.$dispatch('calendar-deleted', { calendarId: this.calendar.id });
        }
        this.closeActionModal();
      } catch (err) {
        this.actionModal.saving = false;
        this.actionModal.open = false;
        alert(err.message);
      }
    },

    formatDate(value) {
      if (!value) return '—';
      return new Date(value).toLocaleString('en-US');
    },
  };
}
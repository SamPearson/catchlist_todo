function calendarCreate() {
  return {
    formData: {
      name: '',
      color: '#767676',
      timezone: '',
    },
    errors: {},
    saving: false,
    expanded: false,

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

    async create() {
      if (!this.validate()) return;
      this.saving = true;
      this.errors.general = '';
      const payload = {
        name: this.formData.name.trim(),
        color: this.formData.color,
      };
      if (this.formData.timezone && this.formData.timezone.trim()) {
        payload.timezone = this.formData.timezone.trim();
      }
      try {
        const cal = await api.post('/api/calendars', payload);
        this.$dispatch('calendar-created', { calendar: cal });
        this.formData = { name: '', color: '#767676', timezone: '' };
        this.expanded = false;
      } catch (err) {
        this.errors.general = err.message;
      } finally {
        this.saving = false;
      }
    },

    cancel() {
      this.formData = { name: '', color: '#767676', timezone: '' };
      this.errors = {};
      this.expanded = false;
    },
  };
}
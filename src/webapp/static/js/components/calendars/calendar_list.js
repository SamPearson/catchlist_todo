function calendarList(initialCalendars) {
  return {
    initialCalendars,
    calendars: initialCalendars,
    error: '',
    eventListenersAdded: false,

    init() {
      if (this.eventListenersAdded) return;
      this.eventListenersAdded = true;
      window.addEventListener('calendar-created', (event) => {
        this.onCalendarCreated(event.detail.calendar);
      });
      window.addEventListener('calendar-updated', (event) => {
        this.onCalendarUpdated(event.detail);
      });
      window.addEventListener('calendar-deleted', (event) => {
        this.onCalendarDeleted(event.detail.calendarId);
      });
    },

    onCalendarCreated(calendar) {
      if (!calendar) return;
      const next = [...this.calendars, calendar];
      this.calendars = next;
      this.initialCalendars = next;
    },

    onCalendarUpdated(calendar) {
      if (!calendar) return;
      this.calendars = this.calendars.map((c) => (c.id === calendar.id ? calendar : c));
      this.initialCalendars = this.initialCalendars.map((c) => (c.id === calendar.id ? calendar : c));
    },

    onCalendarDeleted(calendarId) {
      this.calendars = this.calendars.filter((c) => c.id !== calendarId);
      this.initialCalendars = this.initialCalendars.filter((c) => c.id !== calendarId);
    },
  };
}
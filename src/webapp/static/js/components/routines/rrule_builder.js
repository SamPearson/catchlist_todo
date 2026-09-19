const RruleBuilder = {
  DAY_OPTIONS: [
    { key: 'MO', label: 'Monday' },
    { key: 'TU', label: 'Tuesday' },
    { key: 'WE', label: 'Wednesday' },
    { key: 'TH', label: 'Thursday' },
    { key: 'FR', label: 'Friday' },
    { key: 'SA', label: 'Saturday' },
    { key: 'SU', label: 'Sunday' }
  ],

  empty() {
    return { pattern: 'none', day: 'MO', days: ['MO'], monthDay: 1 };
  },

  dayLabel(d) {
    const opt = this.DAY_OPTIONS.find(o => o.key === d);
    return opt ? opt.label : d;
  },

  parse(rrule) {
    const state = this.empty();
    if (!rrule || typeof rrule !== 'string') return state;
    const freq = /FREQ=([^;]+)/.exec(rrule);
    const byday = /BYDAY=([^;]+)/.exec(rrule);
    const interval = /INTERVAL=(\d+)/.exec(rrule);
    const bymonthday = /BYMONTHDAY=(\d+)/.exec(rrule);
    if (!freq) return state;
    const days = byday ? byday[1].split(',') : [];
    if (freq[1] === 'DAILY') {
      state.pattern = 'daily';
    } else if (freq[1] === 'MONTHLY') {
      state.pattern = 'monthly';
      state.monthDay = parseInt(bymonthday ? bymonthday[1] : '1', 10) || 1;
    } else if (freq[1] === 'WEEKLY') {
      if (interval && parseInt(interval[1], 10) === 2) {
        state.pattern = 'biweekly';
        state.day = days[0] || 'MO';
      } else if (days.length > 1) {
        state.pattern = 'weekdays';
        state.days = days;
      } else {
        state.pattern = 'weekly';
        state.day = days[0] || 'MO';
      }
    } else {
      state.pattern = 'custom';
    }
    return state;
  },

  build(state) {
    if (!state) return '';
    switch (state.pattern) {
      case 'daily':
        return 'FREQ=DAILY';
      case 'weekly':
        return 'FREQ=WEEKLY;BYDAY=' + state.day;
      case 'weekdays':
        return 'FREQ=WEEKLY;BYDAY=' + (state.days && state.days.length ? state.days.join(',') : 'MO');
      case 'biweekly':
        return 'FREQ=WEEKLY;INTERVAL=2;BYDAY=' + state.day;
      case 'monthly':
        return 'FREQ=MONTHLY;BYMONTHDAY=' + (state.monthDay || 1);
      default:
        return '';
    }
  },

  describe(state) {
    if (!state || state.pattern === 'none') return 'Does not repeat';
    switch (state.pattern) {
      case 'daily':
        return 'Every day';
      case 'weekly':
        return 'Every week on ' + this.dayLabel(state.day);
      case 'weekdays':
        return 'Every week on ' + (state.days || []).map(d => this.dayLabel(d)).join(', ');
      case 'biweekly':
        return 'Every 2 weeks on ' + this.dayLabel(state.day);
      case 'monthly':
        return 'Monthly on day ' + (state.monthDay || 1);
      default:
        return 'Custom schedule';
    }
  }
};
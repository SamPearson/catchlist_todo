function routineList(initialRoutines) {
  return {
    initialRoutines: initialRoutines || [],
    routines: initialRoutines || [],
    error: '',
    eventListenersAdded: false,

    init() {
      if (!this.eventListenersAdded) {
        this.eventListenersAdded = true;
        window.addEventListener('routine-created', (event) => this.onRoutineCreated(event));
        window.addEventListener('routine-updated', (event) => this.onRoutineUpdated(event));
        window.addEventListener('routine-deleted', (event) => this.onRoutineDeleted(event));
      }
    },

    onRoutineCreated(event) {
      const routine = event.detail ? event.detail.routine : null;
      if (!routine) return;
      this.routines = [...this.routines, routine];
      this.initialRoutines = [...this.initialRoutines, routine];
    },

    onRoutineUpdated(event) {
      const routine = event.detail ? event.detail.routine : null;
      if (!routine) return;
      this.routines = this.routines.map(r => (r.id === routine.id ? routine : r));
      this.initialRoutines = this.initialRoutines.map(r => (r.id === routine.id ? routine : r));
    },

    onRoutineDeleted(event) {
      const routineId = event.detail ? event.detail.routineId : null;
      if (!routineId) return;
      this.routines = this.routines.filter(r => r.id !== routineId);
      this.initialRoutines = this.initialRoutines.filter(r => r.id !== routineId);
    }
  };
}
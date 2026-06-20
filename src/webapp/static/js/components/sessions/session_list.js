// Session List - Manages a dynamic list of sessions
function sessionList(initialSessions) {
    return {
        initialSessions: initialSessions,
        sessions: initialSessions,
        error: null,

        init() {
            if (!this.eventListenersAdded) {
                window.addEventListener('sessions-search', (e) => this.onSessionsSearch(e));
                this.eventListenersAdded = true;
            }
        },

        onSessionsSearch(event) {
            const { sessions } = event.detail;
            this.sessions = sessions;
            this.error = null;
        }
    };
}
function catchlistEditor() {
    return {
        content: typeof INITIAL_CONTENT !== 'undefined' ? INITIAL_CONTENT : '',
        status: 'idle',          // idle | saving | saved | error
        savedAt: '',
        errorMessage: '',
        _lastSaved: null,
        _timer: null,
        _saving: false,

        init() {
            this._lastSaved = this.content;
            window.addEventListener('beforeunload', () => this.flush());
            document.addEventListener('visibilitychange', () => {
                if (document.visibilityState !== 'visible') this.flush();
            });
        },

        onInput() {
            this.status = 'saving';
            clearTimeout(this._timer);
            this._timer = setTimeout(() => this.save(), 800);
        },

        async save() {
            if (this._saving) {
                return;
            }

            if (this.content === this._lastSaved) {
                this.status = 'idle';
                return;
            }

            this._saving = true;
            this.status = 'saving';
            const snapshot = this.content;

            try {
                const updated = await api.put('/api/catchlist', { content: snapshot });
                this._lastSaved = updated && typeof updated.content === 'string'
                    ? updated.content
                    : snapshot;
                const now = new Date();
                this.savedAt = now.toLocaleTimeString([], { hour: 'numeric', minute: '2-digit' });
                this.status = 'saved';

                // If the user kept typing while we were saving, save again
                if (this.content !== this._lastSaved) {
                    this.status = 'saving';
                    this._timer = setTimeout(() => this.save(), 200);
                }
            } catch (err) {
                this.errorMessage = err.message || 'Could not save your catch list';
                this.status = 'error';
            } finally {
                this._saving = false;
            }
        },

        // Best-effort flush on navigation/tab-hide; keepalive keeps the request alive
        flush() {
            if (this._saving || this.content === this._lastSaved) {
                return;
            }
            clearTimeout(this._timer);
            const payload = JSON.stringify({ content: this.content });
            fetch(`${api.getBaseUrl()}/api/catchlist`, {
                method: 'PUT',
                headers: api.getHeaders(),
                body: payload,
                keepalive: true
            }).then((res) => {
                if (res.ok) {
                    this._lastSaved = this.content;
                }
            }).catch(() => {});
        }
    };
}
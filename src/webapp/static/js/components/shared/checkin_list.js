function checkinList(config) {
    return {
        targetType: config.targetType,
        targetId: config.targetId,
        testid: config.testid,
        checkins: [],
        checkinsExpanded: false,
        showAddCheckin: false,
        checkinsLoading: false,
        newCheckin: { notes: '' },

        init() {
            this.loadCheckins();
        },

        formatDateTime(datetime) {
            if (!datetime) return '';
            const date = new Date(datetime);
            return date.toLocaleString('en-US', { year: 'numeric', month: '2-digit', day: '2-digit', hour: '2-digit', minute: '2-digit', hour12: true });
        },

        async loadCheckins() {
            this.checkinsLoading = true;
            try {
                const checkins = await api.get('/api/checkins/target', {
                    target_type: this.targetType,
                    target_id: this.targetId
                });

                this.checkins = checkins || [];
            } catch (err) {
                console.error('Error loading checkins:', err);
                this.checkins = [];
            } finally {
                this.checkinsLoading = false;
            }
        },

        toggleCheckins() {
            this.checkinsExpanded = !this.checkinsExpanded;
        },

        async addCheckin() {
            if (!this.newCheckin.notes || !this.newCheckin.notes.trim()) {
                alert('Checkin note cannot be empty');
                return;
            }

            try {
                const checkinData = {
                    target_type: this.targetType,
                    target_id: this.targetId,
                    note: this.newCheckin.notes.trim(),
                    occurred_at: new Date().toISOString()
                };

                const createdCheckin = await api.post('/api/checkins', checkinData);

                if (createdCheckin) {
                    this.checkins.unshift(createdCheckin); // Add to front (most recent first)
                    this.newCheckin = { notes: '' };
                    this.showAddCheckin = false;
                }
            } catch (err) {
                console.error('Error adding checkin:', err);
                alert('Error saving checkin: ' + err.message);
            }
        },

        async removeCheckin(index) {
            const checkin = this.checkins[index];
            if (!checkin) return;

            if (!confirm('Are you sure you want to delete this checkin?')) {
                return;
            }

            try {
                await api.delete(`/api/checkins/${checkin.id}`);
                this.checkins.splice(index, 1);
            } catch (err) {
                console.error('Error deleting checkin:', err);
                alert('Error deleting checkin: ' + err.message);
            }
        }
    };
}
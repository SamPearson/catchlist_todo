document.addEventListener('alpine:init', () => {
    Alpine.data('sessionDisplay', (session) => ({
        mode: 'view',
        expanded: false,
        showDeleteModal: false,
        session: session,
        checkins: [],
        checkinsExpanded: false,
        showAddCheckin: false,
        checkinsLoading: false,
        newCheckin: { timestamp: '', notes: '' },
        errors: {},
        submitLoading: false,

        init() {
            this.formData = {
                start_time: this.session.start_time,
                end_time: this.session.end_time,
                status: this.session.status || '',
                notes: this.session.notes || '',
                rpe: this.session.rpe || '',
                routine_name: this.session.routine_name || ''
            };

            // Store original status to detect changes
            this.originalStatus = this.session.status;

            this.formatDate = (datetime) => {
                if (!datetime) return '';
                const date = new Date(datetime);
                return date.toLocaleDateString('en-US', {
                    year: 'numeric',
                    month: '2-digit',
                    day: '2-digit'
                });
            };

            this.formatTime = (datetime) => {
                if (!datetime) return '';
                const date = new Date(datetime);
                return date.toLocaleTimeString('en-US', {
                    hour: '2-digit',
                    minute: '2-digit',
                    hour12: true
                });
            };

            this.formatDateTime = (datetime) => {
                if (!datetime) return '';
                const date = new Date(datetime);
                return date.toLocaleString('en-US', {
                    year: 'numeric',
                    month: '2-digit',
                    day: '2-digit',
                    hour: '2-digit',
                    minute: '2-digit',
                    hour12: true
                });
            };

            this.statusTagClass = () => {
                const classes = 'tag is-medium';
                switch (this.session.status) {
                    case 'scheduled': return `${classes} is-info`;
                    case 'completed': return `${classes} is-success`;
                    case 'skipped': return `${classes} is-warning`;
                    case 'cancelled': return `${classes} is-danger`;
                    default: return classes;
                }
            };

            // Load checkins on init
            this.loadCheckins();
        },

        async loadCheckins() {
            this.checkinsLoading = true;
            try {
                const checkins = await api.get('/api/checkins', {
                    target_type: 'session',
                    target_id: this.session.id
                });

                this.checkins = checkins || [];
            } catch (err) {
                console.error('Error loading checkins:', err);
                this.checkins = [];
            } finally {
                this.checkinsLoading = false;
            }
        },

        toggleEdit() {
            this.mode = this.mode === 'view' ? 'edit' : 'view';
            if (this.mode === 'edit') {
                this.errors = {};
            }
        },

        toggleExpand() {
            this.expanded = !this.expanded;
        },

        toggleCheckins() {
            this.checkinsExpanded = !this.checkinsExpanded;
        },

        async addCheckin() {
            // Validate note is not empty
            if (!this.newCheckin.notes || !this.newCheckin.notes.trim()) {
                alert('Checkin note cannot be empty');
                return;
            }

            try {
                const checkinData = {
                    target_type: 'session',
                    target_id: this.session.id,
                    note: this.newCheckin.notes.trim(),
                    occurred_at: new Date().toISOString()
                };

                const createdCheckin = await api.post('/api/checkins', checkinData);

                if (createdCheckin) {
                    this.checkins.unshift(createdCheckin); // Add to front (most recent first)
                    this.newCheckin = { notes: '' };
                    this.showAddCheckin = false;
                    console.log('Checkin added:', createdCheckin);
                }
            } catch (err) {
                console.error('Error adding checkin:', err);
                alert('Error saving checkin: ' + err.message);
            }
        },

        async removeCheckin(index) {
            const checkin = this.checkins[index];
            if (!checkin) return;

            // Confirm deletion
            if (!confirm('Are you sure you want to delete this checkin?')) {
                return;
            }

            try {
                await api.delete(`/api/checkins/${checkin.id}`);
                this.checkins.splice(index, 1);
                console.log('Checkin removed');
            } catch (err) {
                console.error('Error deleting checkin:', err);
                alert('Error deleting checkin: ' + err.message);
            }
        },

        async submitForm() {
            this.errors = {};
            const requiredFields = ['start_time', 'end_time'];

            // Validate required fields
            requiredFields.forEach(field => {
                if (!this.formData[field]) {
                    this.errors[field] = 'This field is required';
                }
            });

            if (Object.keys(this.errors).length > 0) {
                return;
            }

            this.submitLoading = true;
            try {
                // Prepare patchable fields (only what the API accepts)
                const updateData = {
                    start_time: this.formData.start_time,
                    end_time: this.formData.end_time,
                    notes: this.formData.notes,
                    rpe: this.formData.rpe ? parseInt(this.formData.rpe) : null
                };

                // Update session via PATCH
                const updatedSession = await api.patch(
                    `/api/sessions/${this.session.id}`,
                    updateData
                );

                if (!updatedSession) {
                    this.errors.submit = 'Failed to update session';
                    return;
                }

                // Update local session object with response
                this.session = updatedSession;

                // Handle status change if it occurred
                if (this.formData.status !== this.originalStatus) {
                    const statusUpdate = await api.patch(
                        `/api/sessions/${this.session.id}/status`,
                        { status: this.formData.status }
                    );

                    if (statusUpdate) {
                        this.session = statusUpdate;
                        this.originalStatus = this.formData.status;
                    }
                }

                // Switch back to view mode
                this.mode = 'view';

            } catch (err) {
                console.error('Error updating session:', err);
                this.errors.submit = err.message || 'Error saving session';
            } finally {
                this.submitLoading = false;
            }
        },

        deleteSession() {
            console.log('Session deleted:', this.formData);
            this.showDeleteModal = false;
            this.mode = 'view';
        }
    }));
});
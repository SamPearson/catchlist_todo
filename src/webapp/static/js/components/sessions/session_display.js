document.addEventListener('alpine:init', () => {
    Alpine.data('sessionDisplay', (session) => ({
        mode: 'view',
        expanded: false,
        showDeleteModal: false,
        session: session,
        errors: {},
        submitLoading: false,
        formData: {
            start_time: session.start_time,
            end_time: session.end_time,
            status: session.status || '',
            notes: session.notes || '',
            rpe: session.rpe || '',
            routine_name: session.routine_name || ''
        },
        originalStatus: session.status,

        statusTagClass() {
            switch (this.session.status) {
                case 'scheduled': return 'tag-info';
                case 'completed': return 'tag-success';
                case 'skipped': return 'tag-warning';
                case 'cancelled': return 'tag-danger';
                default: return 'tag-grey';
            }
        },

        formatDate(datetime) {
            if (!datetime) return '';
            const date = new Date(datetime);
            return date.toLocaleDateString('en-US', { year: 'numeric', month: 'short', day: 'numeric' });
        },

        formatTime(datetime) {
            if (!datetime) return '';
            const date = new Date(datetime);
            return date.toLocaleTimeString('en-US', { hour: '2-digit', minute: '2-digit', hour12: true });
        },

        init() {
            // Store original status to detect changes
            this.originalStatus = this.session.status;
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
document.addEventListener('alpine:init', () => {
    Alpine.data('sessionDisplay', (session) => ({
        mode: 'view',
        expanded: false,
        showDeleteModal: false,
        session: session,
        checkins: session.checkins || [],
        checkinsExpanded: false,
        showAddCheckin: false,
        newCheckin: { timestamp: '', notes: '' },
        formData: {
            title: session.title || '',
            start_time: session.start_time
                ? new Date(session.start_time).toISOString().slice(0, 16)
                : '',
            end_time: session.end_time
                ? new Date(session.end_time).toISOString().slice(0, 16)
                : '',
            status: session.status || '',
            notes: session.notes || '',
            rpe: session.rpe || '',
            routine_name: session.routine_name || ''
        },
        errors: {},

        init() {
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
                switch (this.formData.status) {
                    case 'scheduled': return `${classes} is-info`;
                    case 'completed': return `${classes} is-success`;
                    case 'skipped': return `${classes} is-warning`;
                    case 'cancelled': return `${classes} is-danger`;
                    default: return classes;
                }
            };
        },

        toggleEdit() {
            this.mode = this.mode === 'view' ? 'edit' : 'view';
        },

        toggleExpand() {
            this.expanded = !this.expanded;
        },

        toggleCheckins() {
            this.checkinsExpanded = !this.checkinsExpanded;
        },

        addCheckin() {
            const timestamp = new Date().toISOString();
            if (!this.newCheckin.notes && !timestamp) return;
            this.checkins.push({ timestamp, notes: this.newCheckin.notes });
            this.newCheckin = { timestamp: '', notes: '' };
            this.showAddCheckin = false;
            console.log('Checkin added:', this.checkins);
        },

        removeCheckin(index) {
            this.checkins.splice(index, 1);
            console.log('Checkin removed, remaining:', this.checkins);
        },

        submitForm() {
            this.errors = {};
            const requiredFields = ['title', 'start_time', 'end_time'];
            requiredFields.forEach(field => {
                if (!this.formData[field]) {
                    this.errors[field] = 'This field is required';
                }
            });

            if (Object.keys(this.errors).length === 0) {
                console.log('Session updated:', this.formData);
                this.mode = 'view';
            }
        },

        deleteSession() {
            console.log('Session deleted:', this.formData);
            this.showDeleteModal = false;
            this.mode = 'view';
        }
    }));
});
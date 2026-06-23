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
        errors: {},

        formatLocalDateTime(date) {
            const year = date.getFullYear();
            const month = String(date.getMonth() + 1).padStart(2, '0');
            const day = String(date.getDate()).padStart(2, '0');
            const hours = String(date.getHours()).padStart(2, '0');
            const minutes = String(date.getMinutes()).padStart(2, '0');
            return `${year}-${month}-${day}T${hours}:${minutes}`;
        },

        init() {
            this.formData = {
                title: this.session.title || '',
                start_time: this.session.start_time
                    ? this.formatLocalDateTime(new Date(this.session.start_time))
                    : '',
                end_time: this.session.end_time
                    ? this.formatLocalDateTime(new Date(this.session.end_time))
                    : '',
                status: this.session.status || '',
                notes: this.session.notes || '',
                rpe: this.session.rpe || '',
                routine_name: this.session.routine_name || ''
            };

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
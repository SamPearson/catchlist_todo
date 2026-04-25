
// Task Manager - Handles view/edit mode switching for existing tasks
function taskManager(initialTask) {
    return {
        task: initialTask,
        mode: 'view',
        expanded: false,
        formData: {},
        errors: {},
        saving: false,

        edit() {
            this.formData = {
                title: this.task.title,
                description: this.task.description,
                status: this.task.status,
                active: this.task.active
            };
            this.mode = 'edit';
            this.expanded = true;
        },

        toggleExpand() {
            this.expanded = !this.expanded;
        },

        validate() {
            this.errors = {};

            if (!this.formData.title || this.formData.title.trim() === '') {
                this.errors.title = 'Title is required';
                return false;
            }

            if (this.formData.title.length > 200) {
                this.errors.title = 'Title must be 200 characters or less';
                return false;
            }

            return true;
        },

        async save() {
            if (!this.validate()) {
                return;
            }

            this.saving = true;

            try {
                // TODO: Replace with actual API call
                // const result = await api.patch(`/api/tasks/${this.task.id}`, this.formData);

                // Simulate API call
                await new Promise(resolve => setTimeout(resolve, 500));

                console.log('Saving task:', this.formData);

                // Update task with new values
                this.task.title = this.formData.title;
                this.task.description = this.formData.description;
                this.task.status = this.formData.status;
                this.task.active = this.formData.active;
                this.task.updated_at = new Date().toISOString();

                // Switch back to view mode
                this.mode = 'view';

            } catch (err) {
                console.error('Error saving task:', err);
                alert('Error saving task: ' + err.message);
            } finally {
                this.saving = false;
            }
        },

        cancelEdit() {
            this.formData = {};
            this.errors = {};
            this.mode = 'view';
        },

        deleteTask() {
            if (!confirm('Are you sure you want to delete this task? This action cannot be undone.')) {
                return;
            }

            // TODO: Replace with actual API call
            console.log('Deleting task:', this.task.id);
            alert('Task deleted! (This is a demo - no actual deletion)');
        },

        getStatusColor() {
            const statusColors = {
                'open': 'has-text-success',
                'waiting': 'has-text-warning',
                'deferred': 'has-text-info',
                'declined': 'has-text-danger',
                'stale': 'has-text-grey'
            };
            return statusColors[this.task.status] || 'has-text-grey';
        },

        getStatusTagClass() {
            const statusClasses = {
                'open': 'is-success is-light',
                'waiting': 'is-warning is-light',
                'deferred': 'is-info is-light',
                'declined': 'is-danger is-light',
                'stale': 'is-light'
            };
            return statusClasses[this.task.status] || 'is-light';
        },

        formatDate(dateString) {
            if (!dateString) return '';
            const date = new Date(dateString);
            return date.toLocaleString('en-US', {
                year: 'numeric',
                month: 'short',
                day: 'numeric',
                hour: '2-digit',
                minute: '2-digit'
            });
        }
    };
}
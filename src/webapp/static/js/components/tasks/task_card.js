// Task Card - Handles view/edit mode switching for a single task
function taskCard(initialTask) {
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
            let updatedTask = null;
            let partialFailure = false;

            try {
                updatedTask = await api.patch(`/api/tasks/${this.task.id}`, {
                    title: this.formData.title,
                    description: this.formData.description
                });
            } catch (err) {
                console.error('Error saving task fields:', err);
                this.errors.general = 'Error saving task: ' + err.message;
                this.saving = false;
                return;
            }

            if (this.formData.status !== this.task.status) {
                try {
                    updatedTask = await api.patch(`/api/tasks/${this.task.id}/status`, {
                        status: this.formData.status
                    });
                } catch (err) {
                    console.error('Error updating task status:', err);
                    this.errors.general = 'Task fields saved, but status could not be updated: ' + err.message;
                    partialFailure = true;
                }
            }

            if (!partialFailure && this.formData.active !== this.task.active) {
                const activeEndpoint = this.formData.active
                    ? `/api/tasks/${this.task.id}/activate`
                    : `/api/tasks/${this.task.id}/deactivate`;
                try {
                    updatedTask = await api.patch(activeEndpoint);
                } catch (err) {
                    console.error('Error updating task active state:', err);
                    this.errors.general = 'Task fields saved, but active status could not be updated: ' + err.message;
                    partialFailure = true;
                }
            }

            if (partialFailure) {
                try {
                    updatedTask = await api.get(`/api/tasks/${this.task.id}`);
                } catch (err) {
                    console.error('Error reloading task after partial failure:', err);
                }
            }

            if (updatedTask) {
                this.task = updatedTask;
                this.$dispatch('task-updated', updatedTask);
            }

            if (!partialFailure) {
                this.mode = 'view';
            }

            this.saving = false;
        },

        cancelEdit() {
            this.formData = {};
            this.errors = {};
            this.mode = 'view';
        },

        async completeTask() {
            try {
                const updatedTask = await api.patch(`/api/tasks/${this.task.id}/complete`);
                this.task = updatedTask;
                this.$dispatch('task-updated', updatedTask);
            } catch (err) {
                console.error('Error completing task:', err);
                alert('Error completing task: ' + err.message);
            }
        },

        async uncompleteTask() {
            try {
                const updatedTask = await api.patch(`/api/tasks/${this.task.id}/uncomplete`);
                this.task = updatedTask;
                this.$dispatch('task-updated', updatedTask);
            } catch (err) {
                console.error('Error uncompleting task:', err);
                alert('Error uncompleting task: ' + err.message);
            }
        },

        async activateTask() {
            try {
                const updatedTask = await api.patch(`/api/tasks/${this.task.id}/activate`);
                this.task = updatedTask;
                this.$dispatch('task-updated', updatedTask);
            } catch (err) {
                console.error('Error activating task:', err);
                alert('Error activating task: ' + err.message);
            }
        },

        async deleteTask() {
            if (!confirm('Are you sure you want to delete this task? This action cannot be undone.')) {
                return;
            }

            try {
                await api.delete(`/api/tasks/${this.task.id}`);
                this.$dispatch('task-deleted', this.task.id);
            } catch (err) {
                console.error('Error deleting task:', err);
                alert('Error deleting task: ' + err.message);
            }
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
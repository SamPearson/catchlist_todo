// Task Create - Handles creating new tasks
function taskCreate() {
    return {
        formData: {
            title: '',
            description: '',
            status: 'open',
            active: true
        },
        errors: {},
        saving: false,
        expanded: false, // Track expanded/collapsed state

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

        async create() {
            if (!this.validate()) {
                return;
            }

            this.saving = true;

            try {
                const newTask = await api.post('/api/tasks', this.formData);
                console.log('New task created:', newTask);

                // Dispatch custom event with the new task
                this.$dispatch('task-created', { task: newTask });

                // Reset form
                this.formData = {
                    title: '',
                    description: '',
                    status: 'open',
                    active: true
                };

            } catch (err) {
                console.error('Error creating task:', err);
                this.errors.general = 'Error creating task: ' + err.message;
            } finally {
                this.saving = false;
            }
        },

        cancel() {
            this.formData = {
                title: '',
                description: '',
                status: 'open',
                active: true
            };
            this.errors = {};
        }
    };
}
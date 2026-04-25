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
                // TODO: Replace with actual API call
                // const result = await api.post('/api/tasks', this.formData);

                // Simulate API call
                await new Promise(resolve => setTimeout(resolve, 500));

                console.log('Creating task:', this.formData);

                // Create a mock task object with the form data
                const newTask = {
                    id: Math.floor(Math.random() * 1000), // Mock ID
                    ...this.formData,
                    completed: false,
                    completed_at: null,
                    project_id: null,
                    created_at: new Date().toISOString(),
                    updated_at: new Date().toISOString()
                };

                // Dispatch custom event with the new task
                this.$dispatch('task-created', newTask);

                // Reset form
                this.formData = {
                    title: '',
                    description: '',
                    status: 'open',
                    active: true
                };

            } catch (err) {
                console.error('Error creating task:', err);
                alert('Error creating task: ' + err.message);
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
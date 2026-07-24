// Task List - Manages a dynamic list of tasks
function taskList(initialTasks) {
    return {
        initialTasks: initialTasks,
        tasks: initialTasks,
        error: null,

        init() {
            // Alpine's $dispatch bubbles to window, not document
            if (!this.eventListenersAdded) {
                window.addEventListener('task-created', (e) => this.onTaskCreated(e));
                window.addEventListener('task-updated', (e) => this.onTaskUpdated(e));
                window.addEventListener('task-deleted', (e) => this.onTaskDeleted(e));
                window.addEventListener('tasks-search', (e) => this.onTasksSearch(e));
                this.eventListenersAdded = true;

            }

        },

        onTaskCreated(event) {
            // Replace array reference to ensure Alpine's reactivity picks up the change
            this.tasks = [...this.tasks, event.detail.task];
            const newTask = event.detail.task;


        },

        onTaskUpdated(event) {
            const taskId = typeof event.detail === 'number' ? event.detail : event.detail.taskId;
            this.tasks = this.tasks.filter(task => task.id !== taskId);
            this.initialTasks = this.initialTasks.filter(task => task.id !== taskId);
        },

        onTaskDeleted(event) {
            const taskId = event.detail.taskId;
            this.tasks = this.tasks.filter(task => task.id !== taskId);
            this.initialTasks = this.initialTasks.filter(task => task.id !== taskId);
            },

        onTasksSearch(event) {
            const params = event.detail;

            // Always start from the full list of tasks
            this.tasks = [...this.initialTasks];

            // Apply filters
            this.tasks = this.tasks.filter(task => {
                let matches = true;

                // Title filter
                if (params.title) {
                    matches = matches && task.title.toLowerCase().includes(params.title.toLowerCase());
                }

                // Description filter
                if (params.description) {
                    matches = matches && task.description.toLowerCase().includes(params.description.toLowerCase());
                }

                // Status filter
                if (params.status) {
                    const selectedStatuses = params.status.split(',');
                    matches = matches && selectedStatuses.includes(task.status);
                }

                // Active status filter
                if (params.active === 'true') {
                    matches = matches && task.active;
                } else if (params.active === 'false') {
                    matches = matches && !task.active;
                }

                // Completion status filter
                if (params.completed === 'true') {
                    matches = matches && task.completed;
                } else if (params.completed === 'false') {
                    matches = matches && !task.completed;
                }

                return matches;
            });

        }
    };
}
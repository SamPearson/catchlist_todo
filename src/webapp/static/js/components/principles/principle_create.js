// Principle Create - Handles creating new principles
function principleCreate() {
    return {
        formData: {
            title: '',
            description: '',
            reason: '',
            color: '#ffd700'
        },
        errors: {},
        saving: false,
        expanded: false,

        toggleExpand() {
            this.expanded = !this.expanded;
        },

        validate() {
            this.errors = {};

            if (!this.formData.title || this.formData.title.trim() === '') {
                this.errors.title = 'Principle title is required';
                return false;
            }

            if (this.formData.title.length > 50) {
                this.errors.title = 'Principle title must be 50 characters or less';
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
                const payload = {
                    title: this.formData.title.trim(),
                    description: this.formData.description || '',
                    reason: this.formData.reason || '',
                    color: this.formData.color.replace(/^#/, '')
                };
                const newPrinciple = await api.post('/api/principles', payload);
                console.log('New principle created:', newPrinciple);

                this.$dispatch('principle-created', { principle: newPrinciple });

                this.formData = {
                    title: '',
                    description: '',
                    reason: '',
                    color: '#ffd700'
                };
            } catch (err) {
                console.error('Error creating principle:', err);
                this.errors.general = 'Error creating principle: ' + err.message;
            } finally {
                this.saving = false;
            }
        },

        cancel() {
            this.formData = {
                title: '',
                description: '',
                reason: '',
                color: '#ffd700'
            };
            this.errors = {};
        }
    };
}
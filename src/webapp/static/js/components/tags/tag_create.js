// Tag Create - Handles creating new tags
function tagCreate() {
    return {
        formData: {
            name: '',
            color: '#6c757d'
        },
        errors: {},
        saving: false,
        expanded: false,

        toggleExpand() {
            this.expanded = !this.expanded;
        },

        validate() {
            this.errors = {};

            if (!this.formData.name || this.formData.name.trim() === '') {
                this.errors.name = 'Tag name is required';
                return false;
            }

            if (this.formData.name.length > 50) {
                this.errors.name = 'Tag name must be 50 characters or less';
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
                    name: this.formData.name.trim(),
                    color: this.formData.color.replace(/^#/, '')
                };
                const newTag = await api.post('/api/tags', payload);
                console.log('New tag created:', newTag);

                this.$dispatch('tag-created', { tag: newTag });

                this.formData = {
                    name: '',
                    color: '#6c757d'
                };
            } catch (err) {
                console.error('Error creating tag:', err);
                this.errors.general = 'Error creating tag: ' + err.message;
            } finally {
                this.saving = false;
            }
        },

        cancel() {
            this.formData = {
                name: '',
                color: '#6c757d'
            };
            this.errors = {};
        }
    };
}
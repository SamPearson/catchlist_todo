// Principle Card - Handles view/edit mode switching for a single principle
function principleCard(initialPrinciple) {
    return {
        principle: initialPrinciple,
        mode: 'view',
        formData: {},
        errors: {},
        saving: false,

        cssColor(value) {
            if (!value) return 'var(--surface)';
            return value.startsWith('#') ? value : '#' + value;
        },

        edit() {
            this.formData = {
                title: this.principle.title,
                description: this.principle.description || '',
                reason: this.principle.reason || '',
                color: this.cssColor(this.principle.color)
            };
            this.mode = 'edit';
        },

        cancelEdit() {
            this.formData = {};
            this.errors = {};
            this.mode = 'view';
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

        async save() {
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
                const updatedPrinciple = await api.patch(`/api/principles/${this.principle.id}`, payload);
                this.principle = updatedPrinciple;
                this.$dispatch('principle-updated', updatedPrinciple);
                this.mode = 'view';
                this.errors = {};
            } catch (err) {
                console.error('Error saving principle:', err);
                this.errors.general = 'Error saving principle: ' + err.message;
            } finally {
                this.saving = false;
            }
        },

        async deletePrinciple() {
            if (!confirm(`Are you sure you want to delete the principle "${this.principle.title}"? This will remove it from all associated items.`)) {
                return;
            }

            try {
                await api.delete(`/api/principles/${this.principle.id}`);
                this.$dispatch('principle-deleted', { principleId: this.principle.id });
            } catch (err) {
                console.error('Error deleting principle:', err);
                alert('Error deleting principle: ' + err.message);
            }
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
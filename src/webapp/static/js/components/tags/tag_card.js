// Tag Card - Handles view/edit mode switching for a single tag
function tagCard(initialTag) {
    return {
        tag: initialTag,
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
                name: this.tag.name,
                color: this.cssColor(this.tag.color)
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

        async save() {
            if (!this.validate()) {
                return;
            }

            this.saving = true;

            try {
                const payload = {
                    name: this.formData.name.trim(),
                    color: this.formData.color.replace(/^#/, '')
                };
                const updatedTag = await api.patch(`/api/tags/${this.tag.id}`, payload);
                this.tag = updatedTag;
                this.$dispatch('tag-updated', updatedTag);
                this.mode = 'view';
                this.errors = {};
            } catch (err) {
                console.error('Error saving tag:', err);
                this.errors.general = 'Error saving tag: ' + err.message;
            } finally {
                this.saving = false;
            }
        },

        async deleteTag() {
            if (!confirm(`Are you sure you want to delete the tag "${this.tag.name}"? This will remove it from all associated items.`)) {
                return;
            }

            try {
                await api.delete(`/api/tags/${this.tag.id}`);
                this.$dispatch('tag-deleted', { tagId: this.tag.id });
            } catch (err) {
                console.error('Error deleting tag:', err);
                alert('Error deleting tag: ' + err.message);
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
// Tag List - Manages a dynamic list of tags
function tagList(initialTags) {
    return {
        initialTags: initialTags,
        tags: initialTags,
        error: null,

        init() {
            // Alpine's $dispatch bubbles to window, not document
            if (!this.eventListenersAdded) {
                window.addEventListener('tag-created', (e) => this.onTagCreated(e));
                window.addEventListener('tag-updated', (e) => this.onTagUpdated(e));
                window.addEventListener('tag-deleted', (e) => this.onTagDeleted(e));
                this.eventListenersAdded = true;
            }
        },

        onTagCreated(event) {
            // Replace array reference to ensure Alpine's reactivity picks up the change
            this.tags = [...this.tags, event.detail.tag];
            this.initialTags = [...this.initialTags, event.detail.tag];
        },

        onTagUpdated(event) {
            const updatedTag = event.detail;
            this.tags = this.tags.map(tag => (tag.id === updatedTag.id ? updatedTag : tag));
            this.initialTags = this.initialTags.map(tag => (tag.id === updatedTag.id ? updatedTag : tag));
        },

        onTagDeleted(event) {
            const tagId = event.detail.tagId;
            this.tags = this.tags.filter(tag => tag.id !== tagId);
            this.initialTags = this.initialTags.filter(tag => tag.id !== tagId);
        }
    };
}
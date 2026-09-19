function tagPrinciplePicker(config) {
    return {
        targetType: config.targetType,
        targetId: config.targetId,
        testid: config.testid,
        attachedTags: Array.isArray(config.attachedTags) ? config.attachedTags.slice() : [],
        attachedPrinciples: Array.isArray(config.attachedPrinciples) ? config.attachedPrinciples.slice() : [],
        availableTags: [],
        availablePrinciples: [],
        tagQuery: '',
        principleQuery: '',
        tagSearching: false,
        principleSearching: false,
        loading: true,
        error: '',

        init() {
            this.loadPools();
        },

        cssColor(value) {
            if (!value) return 'var(--grey)';
            return value.startsWith('#') ? value : '#' + value;
        },

        async loadPools() {
            try {
                const [tags, principles] = await Promise.all([
                    api.get('/api/tags'),
                    api.get('/api/principles')
                ]);
                this.availableTags = tags || [];
                this.availablePrinciples = principles || [];
            } catch (err) {
                this.error = 'Could not load tags and principles: ' + err.message;
            } finally {
                this.loading = false;
            }
        },

        get tagResults() {
            const attached = new Set(this.attachedTags.map((t) => t.id));
            const q = this.tagQuery.trim().toLowerCase();
            return this.availableTags
                .filter((t) => !attached.has(t.id))
                .filter((t) => !q || t.name.toLowerCase().includes(q));
        },

        get principleResults() {
            const attached = new Set(this.attachedPrinciples.map((p) => p.id));
            const q = this.principleQuery.trim().toLowerCase();
            return this.availablePrinciples
                .filter((p) => !attached.has(p.id))
                .filter((p) => !q || (p.title || '').toLowerCase().includes(q));
        },

        startTagSearch() {
            this.tagSearching = true;
            this.tagQuery = '';
            this.$nextTick(() => {
                if (this.$refs.tagInput) this.$refs.tagInput.focus();
            });
        },

        cancelTagSearch() {
            this.tagSearching = false;
            this.tagQuery = '';
        },

        onTagFocusOut() {
            this.$nextTick(() => {
                if (this.tagSearching) this.cancelTagSearch();
            });
        },

        attachMatchedTag() {
            const match = this.tagResults[0];
            if (match) this.attachTag(match);
        },

        async attachTag(tag) {
            try {
                await api.post('/api/tags/attach', {
                    tag_id: tag.id,
                    target_type: this.targetType,
                    target_id: this.targetId
                });
                this.attachedTags = [...this.attachedTags, tag];
                this.tagQuery = '';
                this.tagSearching = false;
            } catch (err) {
                this.error = err.message;
            }
        },

        async detachTag(tag) {
            try {
                await api.post('/api/tags/detach', {
                    tag_id: tag.id,
                    target_type: this.targetType,
                    target_id: this.targetId
                });
                this.attachedTags = this.attachedTags.filter((t) => t.id !== tag.id);
            } catch (err) {
                this.error = err.message;
            }
        },

        startPrincipleSearch() {
            this.principleSearching = true;
            this.principleQuery = '';
            this.$nextTick(() => {
                if (this.$refs.principleInput) this.$refs.principleInput.focus();
            });
        },

        cancelPrincipleSearch() {
            this.principleSearching = false;
            this.principleQuery = '';
        },

        onPrincipleFocusOut() {
            this.$nextTick(() => {
                if (this.principleSearching) this.cancelPrincipleSearch();
            });
        },

        attachMatchedPrinciple() {
            const match = this.principleResults[0];
            if (match) this.attachPrinciple(match);
        },

        async attachPrinciple(principle) {
            try {
                await api.post('/api/principles/attach', {
                    principle_id: principle.id,
                    target_type: this.targetType,
                    target_id: this.targetId
                });
                this.attachedPrinciples = [...this.attachedPrinciples, principle];
                this.principleQuery = '';
                this.principleSearching = false;
            } catch (err) {
                this.error = err.message;
            }
        },

        async detachPrinciple(principle) {
            try {
                await api.post('/api/principles/detach', {
                    principle_id: principle.id,
                    target_type: this.targetType,
                    target_id: this.targetId
                });
                this.attachedPrinciples = this.attachedPrinciples.filter((p) => p.id !== principle.id);
            } catch (err) {
                this.error = err.message;
            }
        }
    };
}
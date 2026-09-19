// Principle List - Manages a dynamic list of principles
function principleList(initialPrinciples) {
    return {
        initialPrinciples: initialPrinciples,
        principles: initialPrinciples,
        error: null,

        init() {
            // Alpine's $dispatch bubbles to window, not document
            if (!this.eventListenersAdded) {
                window.addEventListener('principle-created', (e) => this.onPrincipleCreated(e));
                window.addEventListener('principle-updated', (e) => this.onPrincipleUpdated(e));
                window.addEventListener('principle-deleted', (e) => this.onPrincipleDeleted(e));
                this.eventListenersAdded = true;
            }
        },

        onPrincipleCreated(event) {
            this.principles = [...this.principles, event.detail.principle];
            this.initialPrinciples = [...this.initialPrinciples, event.detail.principle];
        },

        onPrincipleUpdated(event) {
            const updatedPrinciple = event.detail;
            this.principles = this.principles.map(p => (p.id === updatedPrinciple.id ? updatedPrinciple : p));
            this.initialPrinciples = this.initialPrinciples.map(p => (p.id === updatedPrinciple.id ? updatedPrinciple : p));
        },

        onPrincipleDeleted(event) {
            const principleId = event.detail.principleId;
            this.principles = this.principles.filter(p => p.id !== principleId);
            this.initialPrinciples = this.initialPrinciples.filter(p => p.id !== principleId);
        }
    };
}
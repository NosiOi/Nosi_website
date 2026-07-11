export const TrainingAPI = {
    async getExercises() {
        const r = await fetch("/api/training/exercises");
        return r.json();
    },

    async getPlans() {
        const r = await fetch("/api/training/plans");
        return r.json();
    },

    async savePlan(payload) {
        const r = await fetch("/api/training/plans/save", {
            method: "POST",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify(payload)
        });
        return r.json();
    },

    async completeSession(payload) {
        const r = await fetch("/api/training/session/complete", {
            method: "POST",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify(payload)
        });
        return r.json();
    },

    async getAnalytics() {
        const r = await fetch("/api/training/analytics");
        return r.json();
    },

    async getRecommendations() {
        const r = await fetch("/api/training/recommendations");
        return r.json();
    },

    async getHeatmap(year = new Date().getFullYear()) {
        const r = await fetch(`/api/training/heatmap?year=${year}`);
        return r.json();
    }
};

const TrainingAPI = (() => {
    function fetchJSON(url, options = {}) {
        return fetch(url, {
            credentials: "same-origin",
            headers: { "Content-Type": "application/json" },
            ...options
        }).then(r => {
            if (!r.ok) throw new Error("HTTP " + r.status);
            return r.json();
        });
    }

    function getAnalytics() {
        return fetchJSON("/api/training/analytics");
    }

    function getPlans() {
        return fetchJSON("/api/training/plans");
    }

    function getToday() {
        return fetchJSON("/api/training/today");
    }

    function getTodaySession() {
        return fetchJSON("/api/training/today-session");
    }

    function getRecommendations() {
        return fetchJSON("/api/training/recommendations");
    }

    function getExercises() {
        return fetchJSON("/api/training/exercises?per_page=300");
    }

    function getHeatmap(year) {
        const y = year || new Date().getFullYear();
        return fetchJSON(`/api/training/heatmap?year=${y}`);
    }

    function savePlan(payload) {
        return fetchJSON("/api/training/plans", {
            method: "POST",
            body: JSON.stringify(payload)
        });
    }

    function completeSession(payload) {
        return fetchJSON("/api/training/sessions/complete", {
            method: "POST",
            body: JSON.stringify(payload)
        });
    }

    function strengthTest(payload) {
        return fetchJSON("/api/training/strength-test", {
            method: "POST",
            body: JSON.stringify(payload)
        });
    }

    return {
        getAnalytics,
        getPlans,
        getToday,
        getTodaySession,
        getRecommendations,
        getExercises,
        getHeatmap,
        savePlan,
        completeSession,
        strengthTest
    };
})();

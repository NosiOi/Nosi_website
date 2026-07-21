export const RecoveryAPI = {
    async getSnapshot(userId) {
        const res = await fetch(`/api/recovery/snapshot/${userId}`);
        return res.json();
    },

    async getHeatmap(userId, days = 30) {
        const res = await fetch(`/api/recovery/heatmap/${userId}?days=${days}`);
        return res.json();
    },

    async getRecommendations(userId) {
        const res = await fetch(`/api/recovery/recommendations/${userId}`);
        return res.json();
    },

    async addSleep(userId, sleepStart, sleepEnd) {
        const res = await fetch(`/api/recovery/sleep`, {
            method: "POST",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify({ user_id: userId, sleep_start: sleepStart, sleep_end: sleepEnd })
        });
        return res.json();
    },

    async addHabit(userId, habitId) {
        const res = await fetch(`/api/recovery/habits`, {
            method: "POST",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify({ user_id: userId, habit_id: habitId })
        });
        return res.json();
    },

    async removeHabit(userHabitId) {
        const res = await fetch(`/api/recovery/habits/${userHabitId}`, {
            method: "DELETE"
        });
        return res.json();
    },

    async logHabit(userHabitId) {
        const res = await fetch(`/api/recovery/habits/logs`, {
            method: "POST",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify({ user_habit_id: userHabitId })
        });
        return res.json();
    }
};

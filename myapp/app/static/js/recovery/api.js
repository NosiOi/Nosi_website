const API_BASE = "/api/recovery";

async function request(url, options = {}) {
    const res = await fetch(url, {
        headers: {
            "Content-Type": "application/json",
            ...(options.headers || {})
        },
        ...options
    });

    if (!res.ok) {
        const text = await res.text();
        throw new Error(text || `HTTP ${res.status}`);
    }

    return res.json();
}

export const RecoveryAPI = {
    getSnapshot(userId) {
        return request(`${API_BASE}/snapshot/${userId}`);
    },

    getHeatmap(userId, days = 30) {
        return request(`${API_BASE}/heatmap/${userId}?days=${days}`);
    },

    getRecommendations(userId) {
        return request(`${API_BASE}/recommendations/${userId}`);
    },

    addSleep(userId, sleepStart, sleepEnd) {
        return request(`${API_BASE}/sleep`, {
            method: "POST",
            body: JSON.stringify({
                user_id: userId,
                sleep_start: sleepStart,
                sleep_end: sleepEnd
            })
        });
    },

    addHabit(userId, habitId) {
        return request(`${API_BASE}/habits`, {
            method: "POST",
            body: JSON.stringify({
                user_id: userId,
                habit_id: habitId
            })
        });
    },

    removeHabit(userHabitId) {
        return request(`${API_BASE}/habits/${userHabitId}`, {
            method: "DELETE"
        });
    },

    logHabit(userHabitId) {
        return request(`${API_BASE}/habits/logs`, {
            method: "POST",
            body: JSON.stringify({
                user_habit_id: userHabitId
            })
        });
    }
};

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
        let message = `HTTP ${res.status}`;
        try {
            const contentType = res.headers.get("content-type") || "";
            if (contentType.includes("application/json")) {
                const error = await res.json();
                if (error && error.error) {
                    message = error.error;
                }
            } else {
                const text = await res.text();
                if (text) {
                    message = text;
                }
            }
        } catch (_) {
            // keep default message
        }
        throw new Error(message);
    }

    const contentType = res.headers.get("content-type") || "";
    if (contentType.includes("application/json")) {
        return res.json();
    }

    // no JSON body (e.g. 204)
    return null;
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

    getHabits(userId) {
        return request(`${API_BASE}/habits/${userId}`);
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

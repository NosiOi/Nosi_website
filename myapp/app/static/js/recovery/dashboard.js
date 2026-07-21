import { RecoveryAPI } from "./api.js";
import { renderSleepWidget } from "./sleep.js";
import { renderHabitsWidget } from "./habits.js";
import { renderHeatmapWidget } from "./heatmap.js";
import { renderRecommendationsWidget } from "./recommendations.js";

export async function initRecoveryDashboard(userId) {
    try {
        const snapshot = await RecoveryAPI.getSnapshot(userId);
        const heatmap = await RecoveryAPI.getHeatmap(userId, 30);
        const recommendations = await RecoveryAPI.getRecommendations(userId);

        renderSleepWidget(snapshot);
        renderHabitsWidget(snapshot);
        renderHeatmapWidget(heatmap);
        renderRecommendationsWidget(recommendations);

    } catch (err) {
        console.error("Recovery dashboard error:", err);
    }
}

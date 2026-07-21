import { RecoveryAPI } from "./api.js";
import { renderSleepWidget } from "./sleep.js";
import { renderHabitsWidget } from "./habits.js";
import { renderHeatmapWidget } from "./heatmap.js";
import { renderRecommendationsWidget } from "./recommendations.js";
import { renderScoreWidget } from "./score.js";

export async function initRecoveryDashboard(userId) {
    try {
        const [snapshot, heatmap, recommendations] = await Promise.all([
            RecoveryAPI.getSnapshot(userId),
            RecoveryAPI.getHeatmap(userId, 30),
            RecoveryAPI.getRecommendations(userId)
        ]);

        renderSleepWidget(snapshot);
        renderHabitsWidget(snapshot);
        renderScoreWidget(snapshot);
        renderHeatmapWidget(heatmap);
        renderRecommendationsWidget(recommendations);
    } catch (err) {
        console.error("Recovery dashboard error:", err);
    }
}

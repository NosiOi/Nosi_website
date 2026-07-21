import { RecoveryAPI } from "./api.js";
import { renderSleepWidget } from "./sleep.js";
import { renderHabitsWidget } from "./habits.js";
import { renderHeatmapWidget } from "./heatmap.js";
import { renderRecommendationsWidget } from "./recommendations.js";
import { renderScoreWidget } from "./score.js";

async function loadSnapshot(userId) {
    try {
        return await RecoveryAPI.getSnapshot(userId);
    } catch (err) {
        console.error("Snapshot load error:", err);
        return null;
    }
}

async function loadHeatmap(userId) {
    try {
        return await RecoveryAPI.getHeatmap(userId, 30);
    } catch (err) {
        console.error("Heatmap load error:", err);
        return null;
    }
}

async function loadRecommendations(userId) {
    try {
        return await RecoveryAPI.getRecommendations(userId);
    } catch (err) {
        console.error("Recommendations load error:", err);
        return null;
    }
}

export async function refreshRecoveryDashboard(userId) {
    const [snapshotResult, heatmapResult, recommendationsResult] =
        await Promise.allSettled([
            loadSnapshot(userId),
            loadHeatmap(userId),
            loadRecommendations(userId)
        ]);

    const snapshot =
        snapshotResult.status === "fulfilled" ? snapshotResult.value : null;
    const heatmap =
        heatmapResult.status === "fulfilled" ? heatmapResult.value : null;
    const recommendations =
        recommendationsResult.status === "fulfilled"
            ? recommendationsResult.value
            : null;

    renderSleepWidget(snapshot);
    renderHabitsWidget(snapshot);
    renderScoreWidget(snapshot);
    renderHeatmapWidget(heatmap);
    renderRecommendationsWidget(recommendations);
}

export async function initRecoveryDashboard(userId) {
    try {
        await refreshRecoveryDashboard(userId);
    } catch (err) {
        console.error("Recovery dashboard init error:", err);
    }
}

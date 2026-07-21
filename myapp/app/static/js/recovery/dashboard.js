import { RecoveryAPI } from "./api.js";
import { renderSleepWidget } from "./sleep.js";
import { renderHabitsWidget } from "./habits.js";
import { renderHeatmapWidget } from "./heatmap.js";
import { renderRecommendationsWidget } from "./recommendations.js";
import { renderScoreWidget } from "./score.js";

const DEFAULT_HEATMAP_DAYS = 30;

const state = {
    snapshot: null,
    heatmap: null,
    recommendations: null,
    firstLoad: true
};

function renderLoading() {
    renderSleepWidget(null, { loading: true });
    renderHabitsWidget(null, { loading: true });
    renderScoreWidget(null, { loading: true });
    renderHeatmapWidget(null, { loading: true });
    renderRecommendationsWidget(null, { loading: true });
}

function renderAll() {
    renderSleepWidget(state.snapshot);
    renderHabitsWidget(state.snapshot);
    renderScoreWidget(state.snapshot);
    renderHeatmapWidget(state.heatmap);
    renderRecommendationsWidget(state.recommendations);
}

export async function refreshRecoveryDashboard(userId) {
    if (state.firstLoad) {
        renderLoading();
    }

    const [snapshotRes, heatmapRes, recommendationsRes] =
        await Promise.allSettled([
            RecoveryAPI.getSnapshot(userId),
            RecoveryAPI.getHeatmap(userId, DEFAULT_HEATMAP_DAYS),
            RecoveryAPI.getRecommendations(userId)
        ]);

    state.snapshot = snapshotRes.status === "fulfilled" ? snapshotRes.value : null;
    state.heatmap = heatmapRes.status === "fulfilled" ? heatmapRes.value : null;
    state.recommendations =
        recommendationsRes.status === "fulfilled" ? recommendationsRes.value : null;

    state.firstLoad = false;

    renderAll();
}

export async function initRecoveryDashboard(userId) {
    await refreshRecoveryDashboard(userId);
}

export function destroyRecoveryDashboard() {
    state.snapshot = null;
    state.heatmap = null;
    state.recommendations = null;
    state.firstLoad = true;
}

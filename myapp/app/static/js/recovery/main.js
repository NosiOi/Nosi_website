import { initSleep } from "./sleep.js";
import { initHabits } from "./habits.js";
import { initRecommendations } from "./recommendations.js";
import { initRecoveryHeatmap } from "./heatmap.js";

document.addEventListener("DOMContentLoaded", () => {
    initSleep();
    initHabits();
    initRecommendations();
    initRecoveryHeatmap();
});

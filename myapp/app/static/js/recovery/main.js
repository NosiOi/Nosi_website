import { initRecoveryDashboard } from "./dashboard.js";

document.addEventListener("DOMContentLoaded", () => {
    const root = document.getElementById("recovery-app");
    if (!root) {
        console.error("Recovery root element not found");
        return;
    }

    const rawUserId = root.dataset.userId;
    const userId = Number(rawUserId);

    if (!rawUserId || Number.isNaN(userId)) {
        console.error("User ID not found or invalid in recovery-app dataset");
        return;
    }

    initRecoveryDashboard(userId);
});

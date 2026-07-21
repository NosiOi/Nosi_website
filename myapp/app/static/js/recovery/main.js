import { initRecoveryDashboard } from "./dashboard.js";

document.addEventListener("DOMContentLoaded", () => {
    const root = document.getElementById("recovery-app");
    if (!root) {
        console.error("Recovery root element not found");
        return;
    }

    const userId = root.dataset.userId;
    if (!userId) {
        console.error("User ID not found in recovery-app dataset");
        return;
    }

    initRecoveryDashboard(userId);
});

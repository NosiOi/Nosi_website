import { initRecoveryDashboard } from "./dashboard.js";

document.addEventListener("DOMContentLoaded", () => {
    const userId = window.USER_ID; // ми передамо його з Flask
    if (!userId) {
        console.error("USER_ID не знайдено");
        return;
    }

    initRecoveryDashboard(userId);
});

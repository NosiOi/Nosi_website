import { RecoveryAPI } from "./api.js";
import { refreshRecoveryDashboard } from "./dashboard.js";

export function initSleepModal(userId) {
    const backdrop = document.getElementById("sleep-modal-backdrop");
    const openBtn = document.getElementById("open-sleep-modal");
    const closeBtn = document.querySelector("[data-close-sleep]");
    const saveBtn = document.querySelector("[data-save-sleep]");

    const startInput = document.querySelector("[data-sleep-start]");
    const endInput = document.querySelector("[data-sleep-end]");

    if (!backdrop || !openBtn || !closeBtn || !saveBtn) return;

    const open = () => {
        backdrop.hidden = false;
    };

    const close = () => {
        backdrop.hidden = true;
        startInput.value = "";
        endInput.value = "";
    };

    const save = async () => {
        const start = startInput.value;
        const end = endInput.value;

        if (!start || !end) {
            alert("Будь ласка, заповніть обидва поля");
            return;
        }

        const startDt = new Date(start);
        const endDt = new Date(end);
        const now = new Date();

        if (endDt <= startDt) {
            alert("Кінець сну повинен бути після початку");
            return;
        }

        const durationHours = (endDt - startDt) / 1000 / 3600;

        if (durationHours < 2) {
            alert("Тривалість сну повинна бути не менше 2 годин");
            return;
        }

        if (durationHours > 16) {
            alert("Тривалість сну не може перевищувати 16 годин");
            return;
        }

        if (endDt > now) {
            alert("Сон не може закінчуватися у майбутньому");
            return;
        }

        saveBtn.disabled = true;

        try {
            const res = await RecoveryAPI.addSleep(
                userId,
                startDt.toISOString(),
                endDt.toISOString()
            );

            if (res?.error) {
                alert(res.error);
                return;
            }

            await RecoveryAPI.generateSnapshot(userId);
            await refreshRecoveryDashboard(userId);

            close();
        } finally {
            saveBtn.disabled = false;
        }
    };

    openBtn.addEventListener("click", open);
    closeBtn.addEventListener("click", close);
    saveBtn.addEventListener("click", save);
}

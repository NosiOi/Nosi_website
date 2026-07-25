import { RecoveryAPI } from "../api.js";
import { refreshRecoveryDashboard } from "../dashboard.js";

function toggleHabit(row) {
    row.classList.toggle("selected");
}

export function initHabitModal(userId) {
    const backdrop = document.getElementById("habit-modal-backdrop");
    const openBtn = document.getElementById("open-habit-modal");
    const closeBtn = document.getElementById("close-habit-modal");
    const saveBtn = document.getElementById("save-habit");
    const listBox = document.getElementById("habit-modal-list");

    if (!backdrop || !openBtn || !closeBtn || !saveBtn || !listBox) return;

    const open = async () => {
        backdrop.classList.add("open");

        const habits = await RecoveryAPI.getHabitsList();
        listBox.innerHTML = "";

        habits.forEach(h => {
            const row = document.createElement("div");
            row.className = "habit-row";
            row.dataset.habitId = h.id;
            row.textContent = `${h.name} (+${h.points})`;
            row.addEventListener("click", () => toggleHabit(row));
            listBox.appendChild(row);
        });
    };

    const close = () => {
        backdrop.classList.remove("open");
        listBox.innerHTML = "";
    };

    const save = async () => {
        const selected = [...listBox.querySelectorAll(".habit-row.selected")];
        if (selected.length === 0) {
            alert("Оберіть хоча б одну звичку");
            return;
        }

        saveBtn.disabled = true;

        try {
            for (const row of selected) {
                const habitId = Number(row.dataset.habitId);
                await RecoveryAPI.addHabit(userId, habitId);
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

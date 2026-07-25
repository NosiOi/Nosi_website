import { RecoveryAPI } from "../api.js";
import { refreshRecoveryDashboard } from "../dashboard.js";

let habitsCache = null;
let handlersAttached = false;

async function loadHabits() {
    if (habitsCache) {
        return habitsCache;
    }

    const habits = await RecoveryAPI.getHabitsList();
    habitsCache = Array.isArray(habits) ? habits : [];
    return habitsCache;
}

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

    if (!handlersAttached) {
        openBtn.addEventListener("click", open);
        closeBtn.addEventListener("click", close);
        saveBtn.addEventListener("click", save);
        handlersAttached = true;
    }

    async function open() {
        backdrop.classList.add("open");

        const habits = await loadHabits();
        listBox.innerHTML = "";

        habits.forEach((habit) => {
            const row = document.createElement("div");
            row.className = "habit-row";
            row.dataset.habitId = habit.id;
            row.textContent = `${habit.name} (+${habit.points})`;
            row.addEventListener("click", () => toggleHabit(row));
            listBox.appendChild(row);
        });
    }

    function close() {
        backdrop.classList.remove("open");
        listBox.innerHTML = "";
    }

    async function save() {
        const selected = [...listBox.querySelectorAll(".habit-row.selected")];
        if (selected.length === 0) {
            alert("Оберіть хоча б одну звичку");
            return;
        }

        saveBtn.disabled = true;

        try {
            for (const row of selected) {
                const habitId = Number(row.dataset.habitId);
                if (!Number.isNaN(habitId)) {
                    await RecoveryAPI.addHabit(userId, habitId);
                }
            }

            await RecoveryAPI.generateSnapshot(userId);
            await refreshRecoveryDashboard(userId);

            close();
        } finally {
            saveBtn.disabled = false;
        }
    }
}

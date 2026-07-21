import { RECOVERY_MESSAGES } from "./messages.js";

function clearElement(el) {
    while (el.firstChild) {
        el.removeChild(el.firstChild);
    }
}

export function renderHabitsWidget(snapshot, options = {}) {
    const el = document.getElementById("habits-widget");
    if (!el) return;

    clearElement(el);

    if (options.loading) {
        const loading = document.createElement("div");
        loading.className = "loading";
        loading.textContent = RECOVERY_MESSAGES.loading;
        el.appendChild(loading);
        return;
    }

    if (options.error) {
        const error = document.createElement("div");
        error.className = "error";
        error.textContent = RECOVERY_MESSAGES.error;
        el.appendChild(error);
        return;
    }

    if (!snapshot || snapshot.habit_score == null) {
        const empty = document.createElement("div");
        empty.className = "empty";
        empty.textContent = RECOVERY_MESSAGES.habits.empty;
        el.appendChild(empty);
        return;
    }

    const score = snapshot.habit_score;

    const card = document.createElement("div");
    card.className = "habits-card";

    const title = document.createElement("h3");
    title.textContent = RECOVERY_MESSAGES.habits.title;
    card.appendChild(title);

    const scoreRow = document.createElement("p");
    scoreRow.textContent = `${RECOVERY_MESSAGES.habits.scoreLabel}: `;
    const scoreValue = document.createElement("strong");
    scoreValue.textContent = String(score);
    scoreRow.appendChild(scoreValue);
    card.appendChild(scoreRow);

    el.appendChild(card);
}

import { RECOVERY_MESSAGES } from "./messages.js";

function getScoreClass(score) {
    if (score == null) return "score-neutral";
    if (score < 40) return "score-low";
    if (score < 70) return "score-medium";
    return "score-high";
}

function clearElement(el) {
    while (el.firstChild) {
        el.removeChild(el.firstChild);
    }
}

export function renderScoreWidget(snapshot, options = {}) {
    const el = document.getElementById("score-widget");
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

    if (!snapshot) {
        const empty = document.createElement("div");
        empty.className = "empty";
        empty.textContent = RECOVERY_MESSAGES.score.empty;
        el.appendChild(empty);
        return;
    }

    const recoveryScore = snapshot.recovery_score ?? null;
    const sleepScore = snapshot.sleep_score ?? null;
    const habitScore = snapshot.habit_score ?? null;
    const trainingScore = snapshot.training_score ?? null;
    const energyScore = snapshot.energy_score ?? null;

    const card = document.createElement("div");
    card.className = `score-card ${getScoreClass(recoveryScore)}`;

    const title = document.createElement("h3");
    title.textContent = RECOVERY_MESSAGES.score.title;
    card.appendChild(title);

    const main = document.createElement("p");
    main.className = "score-main";
    const strong = document.createElement("strong");
    strong.textContent = recoveryScore ?? "—";
    main.appendChild(strong);
    card.appendChild(main);

    const breakdown = document.createElement("div");
    breakdown.className = "score-breakdown";

    const sleepRow = document.createElement("div");
    sleepRow.textContent = `${RECOVERY_MESSAGES.score.sleepLabel}: `;
    const sleepValue = document.createElement("span");
    sleepValue.textContent = sleepScore ?? "—";
    sleepRow.appendChild(sleepValue);
    breakdown.appendChild(sleepRow);

    const habitsRow = document.createElement("div");
    habitsRow.textContent = `${RECOVERY_MESSAGES.score.habitsLabel}: `;
    const habitsValue = document.createElement("span");
    habitsValue.textContent = habitScore ?? "—";
    habitsRow.appendChild(habitsValue);
    breakdown.appendChild(habitsRow);

    const trainingRow = document.createElement("div");
    trainingRow.textContent = `${RECOVERY_MESSAGES.score.trainingLabel}: `;
    const trainingValue = document.createElement("span");
    trainingValue.textContent = trainingScore ?? "—";
    trainingRow.appendChild(trainingValue);
    breakdown.appendChild(trainingRow);

    const energyRow = document.createElement("div");
    energyRow.textContent = `${RECOVERY_MESSAGES.score.energyLabel}: `;
    const energyValue = document.createElement("span");
    energyValue.textContent = energyScore ?? "—";
    energyRow.appendChild(energyValue);
    breakdown.appendChild(energyRow);

    card.appendChild(breakdown);
    el.appendChild(card);
}

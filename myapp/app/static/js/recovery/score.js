function getScoreClass(score) {
    if (score == null) return "score-neutral";
    if (score < 40) return "score-low";
    if (score < 70) return "score-medium";
    return "score-high";
}

export function renderScoreWidget(snapshot) {
    const el = document.getElementById("score-widget");
    if (!el) return;

    if (!snapshot) {
        el.innerHTML = `<div class="empty">Немає даних для розрахунку відновлення</div>`;
        return;
    }

    const recoveryScore = snapshot.recovery_score ?? null;
    const sleepScore = snapshot.sleep_score ?? null;
    const habitScore = snapshot.habit_score ?? null;
    const trainingScore = snapshot.training_score ?? null;
    const energyScore = snapshot.energy_score ?? null;

    const scoreClass = getScoreClass(recoveryScore);

    el.innerHTML = `
        <div class="score-card ${scoreClass}">
            <h3>Загальний показник відновлення</h3>
            <p class="score-main">
                <strong>${recoveryScore ?? "—"}</strong>
            </p>
            <div class="score-breakdown">
                <div>Сон: <span>${sleepScore ?? "—"}</span></div>
                <div>Звички: <span>${habitScore ?? "—"}</span></div>
                <div>Тренування: <span>${trainingScore ?? "—"}</span></div>
                <div>Енергія: <span>${energyScore ?? "—"}</span></div>
            </div>
        </div>
    `;
}

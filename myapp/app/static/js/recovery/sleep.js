export function renderSleepWidget(snapshot) {
    const el = document.getElementById("sleep-widget");
    if (!el) return;

    if (!snapshot || snapshot.sleep_score == null) {
        el.innerHTML = `<div class="empty">Немає даних про сон</div>`;
        return;
    }

    const score = snapshot.sleep_score;
    const durationMinutes = snapshot.sleep_duration_minutes ?? null;

    let durationText = "";
    if (durationMinutes != null) {
        const hours = Math.floor(durationMinutes / 60);
        const minutes = durationMinutes % 60;
        durationText = `${hours}h ${minutes}m`;
    }

    el.innerHTML = `
        <div class="sleep-card">
            <h3>Сон</h3>
            <p>Оцінка: <strong>${score}</strong></p>
            ${durationText ? `<p>Тривалість: <strong>${durationText}</strong></p>` : ""}
        </div>
    `;
}

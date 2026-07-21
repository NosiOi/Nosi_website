function formatTime(value) {
    if (!value) return "";
    try {
        const date = new Date(value);
        return date.toLocaleTimeString("uk-UA", {
            hour: "2-digit",
            minute: "2-digit"
        });
    } catch (_) {
        return value;
    }
}

export function renderSleepWidget(snapshot) {
    const el = document.getElementById("sleep-widget");
    if (!el) return;

    if (!snapshot || snapshot.sleep_score == null) {
        el.innerHTML = `<div class="empty">Немає даних про сон</div>`;
        return;
    }

    const score = snapshot.sleep_score;

    el.innerHTML = `
        <div class="sleep-card">
            <h3>Сон</h3>
            <p>Оцінка: <strong>${score}</strong></p>
            <!-- TODO: додати тривалість і період сну, коли API повертає ці поля -->
        </div>
    `;
}

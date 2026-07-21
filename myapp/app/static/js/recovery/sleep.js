export function renderSleepWidget(snapshot) {
    const el = document.getElementById("sleep-widget");
    if (!el) return;

    if (!snapshot || !snapshot.sleep_score) {
        el.innerHTML = `<div class="empty">Немає даних про сон</div>`;
        return;
    }

    el.innerHTML = `
        <div class="sleep-card">
            <h3>Сон</h3>
            <p>Оцінка: <strong>${snapshot.sleep_score}</strong></p>
        </div>
    `;
}

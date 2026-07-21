export function renderHabitsWidget(snapshot) {
    const el = document.getElementById("habits-widget");
    if (!el) return;

    if (!snapshot || !snapshot.habit_score) {
        el.innerHTML = `<div class="empty">Звички ще не додані</div>`;
        return;
    }

    el.innerHTML = `
        <div class="habits-card">
            <h3>Звички</h3>
            <p>Оцінка: <strong>${snapshot.habit_score}</strong></p>
        </div>
    `;
}

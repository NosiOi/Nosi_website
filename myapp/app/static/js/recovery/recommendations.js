export function renderRecommendationsWidget(data) {
    const el = document.getElementById("recommendations-widget");
    if (!el) return;

    if (!data || !data.recommendations) {
        el.innerHTML = `<div class="empty">Немає рекомендацій</div>`;
        return;
    }

    const list = data.recommendations.map(r => `<li>${r}</li>`).join("");

    el.innerHTML = `
        <div class="recommendations-card">
            <h3>Рекомендації</h3>
            <ul>${list}</ul>
        </div>
    `;
}

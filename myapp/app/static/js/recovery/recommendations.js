export function renderRecommendationsWidget(data) {
    const el = document.getElementById("recommendations-widget");
    if (!el) return;

    const recommendations = data?.recommendations ?? null;

    if (!recommendations || !Array.isArray(recommendations) || recommendations.length === 0) {
        el.innerHTML = `<div class="empty">Немає рекомендацій</div>`;
        return;
    }

    const list = recommendations.map(r => `<li>${r}</li>`).join("");

    el.innerHTML = `
        <div class="recommendations-card">
            <h3>Рекомендації</h3>
            <ul>${list}</ul>
        </div>
    `;
}

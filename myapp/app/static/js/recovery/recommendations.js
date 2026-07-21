export function renderRecommendationsWidget(data) {
    const el = document.getElementById("recommendations-widget");
    if (!el) return;

    const recommendations = data?.recommendations ?? null;

    if (!recommendations || !Array.isArray(recommendations) || recommendations.length === 0) {
        el.innerHTML = `<div class="empty">Немає рекомендацій</div>`;
        return;
    }

    const container = document.createElement("div");
    container.className = "recommendations-card";

    const title = document.createElement("h3");
    title.textContent = "Рекомендації";
    container.appendChild(title);

    const list = document.createElement("ul");

    recommendations.forEach((text) => {
        const li = document.createElement("li");
        li.textContent = text;
        list.appendChild(li);
    });

    container.appendChild(list);

    el.innerHTML = "";
    el.appendChild(container);
}

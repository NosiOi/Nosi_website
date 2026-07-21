import { RECOVERY_MESSAGES } from "./messages.js";

function clearElement(el) {
    while (el.firstChild) {
        el.removeChild(el.firstChild);
    }
}

export function renderRecommendationsWidget(data, options = {}) {
    const el = document.getElementById("recommendations-widget");
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

    const recommendations = data?.recommendations ?? null;

    if (!recommendations || !Array.isArray(recommendations) || recommendations.length === 0) {
        const empty = document.createElement("div");
        empty.className = "empty";
        empty.textContent = RECOVERY_MESSAGES.recommendations.empty;
        el.appendChild(empty);
        return;
    }

    const card = document.createElement("div");
    card.className = "recommendations-card";

    const title = document.createElement("h3");
    title.textContent = RECOVERY_MESSAGES.recommendations.title;
    card.appendChild(title);

    const list = document.createElement("ul");

    recommendations.forEach((text) => {
        const li = document.createElement("li");
        li.textContent = text;
        list.appendChild(li);
    });

    card.appendChild(list);
    el.appendChild(card);
}

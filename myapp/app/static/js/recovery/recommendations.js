import { RECOVERY_MESSAGES } from "./messages.js";
import { ICONS } from "../icons/icons.js";
import {
    clearElement,
    createCard,
    createTitle,
    createLoading,
    createError,
    createEmpty
} from "./dom.js";

const PRIORITY_ORDER = {
    high: 1,
    medium: 2,
    low: 3
};

export function renderRecommendationsWidget(data, options = {}) {
    const el = document.getElementById("recommendations-widget");
    if (!el) return;

    clearElement(el);

    if (options.loading) {
        el.appendChild(createLoading(RECOVERY_MESSAGES.loading));
        return;
    }

    if (options.error) {
        el.appendChild(createError(RECOVERY_MESSAGES.error));
        return;
    }

    const recommendations = Array.isArray(data?.recommendations)
        ? data.recommendations
        : [];

    if (recommendations.length === 0) {
        el.appendChild(createEmpty(RECOVERY_MESSAGES.recommendations.empty));
        return;
    }

    const card = createCard("recommendations-card");
    card.appendChild(createTitle(RECOVERY_MESSAGES.recommendations.title));

    const container = document.createElement("div");
    container.className = "recommendations-content";

    const sorted = recommendations.sort(
        (a, b) => PRIORITY_ORDER[a.priority] - PRIORITY_ORDER[b.priority]
    );

    sorted.forEach(rec => {
        const item = document.createElement("div");
        item.className = "recommendation-item";

        const iconWrap = document.createElement("div");
        iconWrap.className = "recommendation-icon";
        iconWrap.innerHTML = ICONS[rec.icon] || "";

        const textWrap = document.createElement("div");
        textWrap.className = "recommendation-text";
        textWrap.textContent = rec.text;

        item.appendChild(iconWrap);
        item.appendChild(textWrap);

        container.appendChild(item);
    });

    card.appendChild(container);
    el.appendChild(card);
}

import { RECOVERY_MESSAGES } from "./messages.js";
import {
    clearElement,
    createCard,
    createTitle,
    createLoading,
    createError,
    createEmpty
} from "./dom.js";

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

    const recommendations = data?.recommendations ?? null;

    if (!recommendations || !Array.isArray(recommendations) || recommendations.length === 0) {
        el.appendChild(createEmpty(RECOVERY_MESSAGES.recommendations.empty));
        return;
    }

    const card = createCard("recommendations-card");
    card.appendChild(createTitle(RECOVERY_MESSAGES.recommendations.title));

    const list = document.createElement("ul");

    recommendations.forEach((text) => {
        const li = document.createElement("li");
        li.textContent = text;
        list.appendChild(li);
    });

    card.appendChild(list);
    el.appendChild(card);
}

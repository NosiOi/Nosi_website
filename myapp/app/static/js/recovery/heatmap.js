import { RECOVERY_MESSAGES } from "./messages.js";

function clearElement(el) {
    while (el.firstChild) {
        el.removeChild(el.firstChild);
    }
}

export function renderHeatmapWidget(heatmap, options = {}) {
    const el = document.getElementById("heatmap-widget");
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

    if (!heatmap || !Array.isArray(heatmap) || heatmap.length === 0) {
        const empty = document.createElement("div");
        empty.className = "empty";
        empty.textContent = RECOVERY_MESSAGES.heatmap.empty;
        el.appendChild(empty);
        return;
    }

    const card = document.createElement("div");
    card.className = "heatmap-card";

    const title = document.createElement("h3");
    title.textContent = RECOVERY_MESSAGES.heatmap.title;
    card.appendChild(title);

    const daysRow = document.createElement("p");
    daysRow.textContent = `${RECOVERY_MESSAGES.heatmap.daysLabel}: `;
    const daysValue = document.createElement("strong");
    daysValue.textContent = String(heatmap.length);
    daysRow.appendChild(daysValue);
    card.appendChild(daysRow);

    el.appendChild(card);
}

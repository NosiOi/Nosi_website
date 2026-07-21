import { RECOVERY_MESSAGES } from "./messages.js";
import {
    clearElement,
    createCard,
    createTitle,
    createLabelValue,
    createLoading,
    createError,
    createEmpty
} from "./dom.js";

export function renderHeatmapWidget(heatmap, options = {}) {
    const el = document.getElementById("heatmap-widget");
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

    if (!heatmap || !Array.isArray(heatmap) || heatmap.length === 0) {
        el.appendChild(createEmpty(RECOVERY_MESSAGES.heatmap.empty));
        return;
    }

    const card = createCard("heatmap-card");
    card.appendChild(createTitle(RECOVERY_MESSAGES.heatmap.title));
    card.appendChild(createLabelValue(RECOVERY_MESSAGES.heatmap.daysLabel, heatmap.length));

    // TODO(recovery): render calendar heatmap

    el.appendChild(card);
}

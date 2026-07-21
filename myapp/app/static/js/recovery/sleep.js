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

export function renderSleepWidget(snapshot, options = {}) {
    const el = document.getElementById("sleep-widget");
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

    if (!snapshot || snapshot.sleep_score == null) {
        el.appendChild(createEmpty(RECOVERY_MESSAGES.sleep.empty));
        return;
    }

    const card = createCard("sleep-card");
    card.appendChild(createTitle(RECOVERY_MESSAGES.sleep.title));
    card.appendChild(createLabelValue("Оцінка", snapshot.sleep_score));

    // TODO(recovery): add duration and time range when API supports these fields

    el.appendChild(card);
}

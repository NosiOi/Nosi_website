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

export function renderHabitsWidget(snapshot, options = {}) {
    const el = document.getElementById("habits-widget");
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

    if (!snapshot || snapshot.habit_score == null) {
        el.appendChild(createEmpty(RECOVERY_MESSAGES.habits.empty));
        return;
    }

    const card = createCard("habits-card");
    card.appendChild(createTitle(RECOVERY_MESSAGES.habits.title));
    card.appendChild(createLabelValue("Оцінка", snapshot.habit_score));

    el.appendChild(card);
}

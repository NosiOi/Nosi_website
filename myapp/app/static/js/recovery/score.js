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

const LOW_SCORE = 40;
const MEDIUM_SCORE = 70;

/**
 * @param {number|null} score
 * @returns {string}
 */
function getScoreClass(score) {
    if (score == null) return "score-neutral";
    if (score < LOW_SCORE) return "score-low";
    if (score < MEDIUM_SCORE) return "score-medium";
    return "score-high";
}

export function renderScoreWidget(snapshot, options = {}) {
    const el = document.getElementById("score-widget");
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

    if (!snapshot) {
        el.appendChild(createEmpty(RECOVERY_MESSAGES.score.empty));
        return;
    }

    const card = createCard(`score-card ${getScoreClass(snapshot.recovery_score)}`);
    card.appendChild(createTitle(RECOVERY_MESSAGES.score.title));

    card.appendChild(createLabelValue("Показник", snapshot.recovery_score ?? "—"));
    card.appendChild(createLabelValue("Сон", snapshot.sleep_score ?? "—"));
    card.appendChild(createLabelValue("Звички", snapshot.habit_score ?? "—"));
    card.appendChild(createLabelValue("Тренування", snapshot.training_score ?? "—"));
    card.appendChild(createLabelValue("Енергія", snapshot.energy_score ?? "—"));

    el.appendChild(card);
}

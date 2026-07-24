import { RECOVERY_MESSAGES } from "./messages.js";
import {
    clearElement,
    createCard,
    createTitle,
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

    if (!snapshot || snapshot.sleep_score == null || snapshot.sleep_duration_minutes == null) {
        el.appendChild(createEmpty(RECOVERY_MESSAGES.sleep.empty));
        return;
    }

    const card = createCard("sleep-card");

    const durationHours = Math.floor(snapshot.sleep_duration_minutes / 60);
    const durationMinutes = snapshot.sleep_duration_minutes % 60;

    const start = new Date(snapshot.sleep_start);
    const end = new Date(snapshot.sleep_end);

    const startStr = start.toLocaleTimeString("uk-UA", { hour: "2-digit", minute: "2-digit" });
    const endStr = end.toLocaleTimeString("uk-UA", { hour: "2-digit", minute: "2-digit" });

    const status =
        snapshot.sleep_duration_minutes >= 480 ? "Відмінний сон" :
        snapshot.sleep_duration_minutes >= 420 ? "Добрий сон" :
        snapshot.sleep_duration_minutes >= 360 ? "Достатній сон" :
        "Недосип";

    card.innerHTML = `
        <div class="sleep-content">
            <div class="sleep-duration">${durationHours} год ${durationMinutes} хв</div>

            <div class="sleep-range">${startStr} → ${endStr}</div>

            <div class="sleep-score-bar">
                <div class="sleep-score-fill" style="width:${snapshot.sleep_score}%"></div>
            </div>

            <div class="sleep-status">${status}</div>
        </div>
    `;

    el.appendChild(card);
}

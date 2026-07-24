import { RECOVERY_MESSAGES } from "./messages.js";
import {
    clearElement,
    createCard,
    createTitle,
    createLoading,
    createError,
    createEmpty
} from "./dom.js";

function getSleepStatus(minutes) {
    if (!minutes || minutes <= 0) return "Немає даних";

    if (minutes >= 480) return "Відмінний сон";
    if (minutes >= 420) return "Добрий сон";
    if (minutes >= 360) return "Достатній сон";
    return "Недосип";
}

function getSleepRecencyLabel(snapshotDateIso) {
    if (!snapshotDateIso) return "";

    const snapshotDate = new Date(snapshotDateIso);
    const today = new Date();

    const snap = new Date(
        snapshotDate.getFullYear(),
        snapshotDate.getMonth(),
        snapshotDate.getDate()
    );
    const now = new Date(
        today.getFullYear(),
        today.getMonth(),
        today.getDate()
    );

    const diffDays = Math.round((now - snap) / (1000 * 60 * 60 * 24));

    if (diffDays === 0) return "Останній запис: сьогодні";
    if (diffDays === 1) return "Останній запис: вчора";

    return `Останній запис: ${snapshotDate.toLocaleDateString("uk-UA", {
        day: "numeric",
        month: "long",
        year: "numeric"
    })}`;
}

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

    if (
        !snapshot ||
        snapshot.sleep_score == null ||
        snapshot.sleep_duration_minutes == null ||
        !snapshot.sleep_start ||
        !snapshot.sleep_end
    ) {
        el.appendChild(createEmpty(RECOVERY_MESSAGES.sleep.empty));
        return;
    }

    const card = createCard("sleep-card");
    card.appendChild(createTitle(RECOVERY_MESSAGES.sleep.title));

    const content = document.createElement("div");
    content.className = "sleep-content";

    const durationHours = Math.floor(snapshot.sleep_duration_minutes / 60);
    const durationMinutes = snapshot.sleep_duration_minutes % 60;

    const start = new Date(snapshot.sleep_start);
    const end = new Date(snapshot.sleep_end);

    const startStr = start.toLocaleTimeString("uk-UA", {
        hour: "2-digit",
        minute: "2-digit"
    });
    const endStr = end.toLocaleTimeString("uk-UA", {
        hour: "2-digit",
        minute: "2-digit"
    });

    const statusText = getSleepStatus(snapshot.sleep_duration_minutes);
    const recencyText = getSleepRecencyLabel(snapshot.date);

    const durationEl = document.createElement("div");
    durationEl.className = "sleep-duration";
    durationEl.textContent = `${durationHours} год ${durationMinutes} хв`;

    const rangeEl = document.createElement("div");
    rangeEl.className = "sleep-range";
    rangeEl.textContent = `${startStr} → ${endStr}`;

    const bar = document.createElement("div");
    bar.className = "sleep-score-bar";

    const fill = document.createElement("div");
    fill.className = "sleep-score-fill";
    fill.style.width = `${snapshot.sleep_score}%`;
    bar.appendChild(fill);

    const statusEl = document.createElement("div");
    statusEl.className = "sleep-status";
    statusEl.textContent = statusText;

    const metaEl = document.createElement("div");
    metaEl.className = "sleep-meta";
    metaEl.textContent = recencyText;

    content.appendChild(durationEl);
    content.appendChild(rangeEl);
    content.appendChild(bar);
    content.appendChild(statusEl);
    if (recencyText) {
        content.appendChild(metaEl);
    }

    card.appendChild(content);
    el.appendChild(card);
}

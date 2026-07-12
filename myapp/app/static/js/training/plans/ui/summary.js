import { state } from "../state.js";
import { dom } from "../dom.js";
import { formatSets, formatCount } from "../utils.js";

export function updateSummary(list) {
    const count = formatCount(list);
    const sets = formatSets(list);

    dom.summaryCount.textContent = `${count} вправ`;
    dom.summarySets.textContent = `${sets} підходів`;

    dom.daySummary.textContent = count ? `${count} вправ, ${sets} підходів` : "План порожній";

    updateBadges();
}

function updateBadges() {
    dom.dayButtons.forEach(btn => {
        const day = btn.dataset.day;
        const badge = btn.querySelector(".tr-plan-day-badge");
        if (!badge) return;
        const count = state.days[day].length;
        if (count > 0) {
            badge.textContent = count;
            badge.classList.add("visible");
        } else {
            badge.textContent = "";
            badge.classList.remove("visible");
        }
    });
}

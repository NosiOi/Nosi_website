import { state } from "../state.js";
import { formatSets, formatCount } from "../utils.js";

export function updateSummary(list) {
    const count = formatCount(list);
    const sets = formatSets(list);

    document.getElementById("tr-plan-summary-count").textContent = `${count} вправ`;
    document.getElementById("tr-plan-summary-sets").textContent = `${sets} підходів`;

    const daySummary = document.getElementById("tr-plan-day-summary");
    daySummary.textContent = count ? `${count} вправ, ${sets} підходів` : "План порожній";

    updateBadges();
}

function updateBadges() {
    const badges = document.querySelectorAll(".tr-plan-day-badge");
    badges.forEach(b => {
        const day = b.dataset.dayBadge;
        const count = state.days[day].length;
        if (count > 0) {
            b.textContent = count;
            b.classList.add("visible");
        } else {
            b.textContent = "";
            b.classList.remove("visible");
        }
    });
}

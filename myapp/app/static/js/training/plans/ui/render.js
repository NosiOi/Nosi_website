import { state } from "../state.js";
import { createExerciseCard } from "./cards/exerciseCard.js";
import { updateSummary } from "./summary.js";

export function renderExercises(container, openPicker) {
    container.innerHTML = "";
    const list = state.days[state.currentDay];

    const emptyState = document.getElementById("tr-plan-empty");
    if (!list.length) {
        emptyState.classList.add("visible");
        updateSummary(list);
        return;
    }

    emptyState.classList.remove("visible");

    list.forEach((ex, index) => {
        const card = createExerciseCard(ex, index, list, () => renderExercises(container, openPicker), openPicker);
        container.appendChild(card);
    });

    updateSummary(list);
}

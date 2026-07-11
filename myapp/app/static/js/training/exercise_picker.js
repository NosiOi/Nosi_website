import { trainingStore } from "./store.js";
import { renderWorkoutList } from "./workout.js";

export function openExercisePicker(callback) {
    const modal = document.getElementById("tr-exercise-picker-modal");
    const list = document.getElementById("tr-ex-list");
    const search = document.getElementById("tr-ex-search");
    if (!modal || !list) return;

    const renderList = items => {
        list.innerHTML = "";
        items.forEach(ex => {
            const row = document.createElement("div");
            row.className = "tr-ex-modal-item";
            row.textContent = ex.name;
            row.onclick = () => {
                callback(ex);
                modal.classList.remove("open");
            };
            list.appendChild(row);
        });
    };

    renderList(trainingStore.exercises);

    if (search) {
        search.value = "";
        search.oninput = () => {
            const q = search.value.trim().toLowerCase();
            if (!q) renderList(trainingStore.exercises);
            else renderList(trainingStore.exercises.filter(ex => ex.name.toLowerCase().includes(q)));
        };
    }

    modal.classList.add("open");
}

document.addEventListener("click", e => {
    if (e.target && e.target.matches("[data-close-exercise-picker]")) {
        const modal = document.getElementById("tr-exercise-picker-modal");
        if (modal) modal.classList.remove("open");
    }
});

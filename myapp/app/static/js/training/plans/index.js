import { initState, state } from "./state.js";
import { renderExercises } from "./ui/render.js";
import { savePlan } from "./services/save.js";
import { openExercisePicker } from "../exercise_picker.js";

export function initPlanModal() {
    const modal = document.getElementById("tr-plan-modal");
    const saveBtn = document.getElementById("tr-plan-save");
    const titleInput = document.getElementById("tr-plan-title");
    const dayButtons = document.querySelectorAll(".tr-plan-day");
    const container = document.querySelector(".tr-plan-exercises");
    const addBtn = document.querySelector(".tr-plan-add-exercise");
    const emptyAddBtn = document.querySelector(".tr-plan-empty-add");
    const helpToggle = document.getElementById("tr-plan-help-toggle");
    const helpPopover = document.getElementById("tr-plan-help");

    initState();

    dayButtons.forEach(btn => {
        btn.onclick = () => {
            state.currentDay = btn.dataset.day;
            dayButtons.forEach(b => b.classList.remove("active"));
            btn.classList.add("active");
            renderExercises(container, openExercisePicker);
        };
    });

    addBtn.onclick = () => {
        openExercisePicker(ex => {
            state.days[state.currentDay].push({
                exercise: ex,
                sets: 3,
                reps: "8–12",
                load: 0
            });
            renderExercises(container, openExercisePicker);
        });
    };

    emptyAddBtn.onclick = () => addBtn.click();

    helpToggle.onclick = () => {
        helpPopover.classList.toggle("open");
    };

    saveBtn.onclick = () => savePlan(titleInput.value, modal);

    const openBtn = document.getElementById("tr-edit-plan");
    if (openBtn) {
        openBtn.onclick = () => {
            initState(true);
            titleInput.value = window.trainingStore.plan?.name || "Мій план";
            renderExercises(container, openExercisePicker);
            modal.classList.add("open");
        };
    }

    const closeBtns = document.querySelectorAll("[data-close-plan]");
    closeBtns.forEach(btn => {
        btn.onclick = () => modal.classList.remove("open");
    });
}

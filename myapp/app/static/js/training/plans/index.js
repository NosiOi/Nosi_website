import { initState, state } from "./state.js";
import { dom } from "./dom.js";
import { renderExercises } from "./ui/render.js";
import { savePlan } from "./services/save.js";
import { openExercisePicker } from "../exercise_picker.js";

export function initPlanModal() {
    initState();

    dom.dayButtons.forEach(btn => {
        btn.onclick = () => {
            state.currentDay = btn.dataset.day;
            dom.dayButtons.forEach(b => b.classList.remove("active"));
            btn.classList.add("active");
            renderExercises(openExercisePicker);
        };
    });

    dom.addBtn.onclick = () => {
        openExercisePicker(ex => {
            state.days[state.currentDay].push({
                exercise: ex,
                sets: 3,
                reps: "8–12",
                load: 0
            });
            renderExercises(openExercisePicker);
        });
    };

    dom.emptyAddBtn.onclick = () => dom.addBtn.click();

    dom.helpToggle.onclick = () =>
        dom.helpPopover.classList.toggle("open");

    dom.saveBtn.onclick = () => savePlan();

    if (dom.openBtn) {
        dom.openBtn.onclick = () => {
            initState(true);
            dom.titleInput.value = window.trainingStore.plan?.name || "Мій план";
            renderExercises(openExercisePicker);
            dom.modal.classList.add("open");
        };
    }

    dom.closeBtns.forEach(btn => {
        btn.onclick = () => dom.modal.classList.remove("open");
    });
}

import { initState, state } from "./state.js";
import { dom } from "./dom.js";
import { DAYS } from "./constants.js";
import { renderExercises } from "./ui/render.js";
import { savePlan } from "./services/save.js";
import { openExercisePicker } from "../exercise_picker.js";

function renderDays() {
    const container = document.getElementById("tr-plan-days");
    container.innerHTML = "";

    DAYS.forEach(day => {
        const btn = document.createElement("button");
        btn.className = "tr-plan-day";
        btn.dataset.day = day.key;
        btn.innerHTML = `
            <span>${day.short}</span>
            <span class="tr-plan-day-badge" data-day-badge="${day.key}"></span>
        `;
        container.appendChild(btn);
    });

    dom.dayButtons = container.querySelectorAll(".tr-plan-day");
}

export function initPlanModal() {
    renderDays();
    initState();

    dom.dayButtons.forEach(btn => {
        btn.onclick = () => {
            state.currentDay = btn.dataset.day;
            dom.dayButtons.forEach(b => b.classList.remove("active"));
            btn.classList.add("active");
            renderExercises(openExercisePicker);
        };
    });

    if (dom.addBtn) {
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
    }

    if (dom.emptyAddBtn) {
        dom.emptyAddBtn.onclick = () => dom.addBtn?.click();
    }

    if (dom.helpToggle) {
        dom.helpToggle.onclick = () => {
            dom.helpPopover.classList.toggle("open");
        };
    }

    if (dom.saveBtn) {
        dom.saveBtn.onclick = () => savePlan();
    }

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

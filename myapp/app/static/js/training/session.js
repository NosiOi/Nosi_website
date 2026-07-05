const PlanModal = (() => {
    const modal = document.getElementById("tr-plan-modal");
    const saveBtn = document.getElementById("tr-plan-save");
    const closeBtns = document.querySelectorAll("[data-close-plan]");
    const dayButtons = document.querySelectorAll(".tr-plan-day");
    const exercisesContainer = document.querySelector(".tr-plan-exercises");
    const addExerciseBtn = document.querySelector(".tr-plan-add-exercise");

    let currentPlan = { name: "Мій план", days: {} };
    let activeDay = "mon";

    const daysOrder = ["mon","tue","wed","thu","fri","sat","sun"];

    function ensureStructure() {
        if (!currentPlan.days) currentPlan.days = {};
        daysOrder.forEach(k => {
            if (!currentPlan.days[k]) currentPlan.days[k] = { exercises: [] };
        });
    }

    function open() {
        TrainingAPI.getPlans().then(plans => {
            if (!plans.length) {
                currentPlan = { name: "Мій план", days: {} };
            } else {
                const active = plans.find(p => p.is_active) || plans[0];
                currentPlan = { name: active.name || "Мій план", days: active.days || {} };
            }

            ensureStructure();
            renderDays();
            setActiveDay("mon");
            modal.classList.add("open");
        });
    }

    function close() {
        modal.classList.remove("open");
    }

    function renderDays() {
        dayButtons.forEach(btn => {
            btn.onclick = () => {
                saveCurrentDayExercises();
                setActiveDay(btn.dataset.day);
            };
        });
    }

    function setActiveDay(day) {
        activeDay = day;
        dayButtons.forEach(b => b.classList.remove("active"));
        const activeBtn = document.querySelector(`.tr-plan-day[data-day="${day}"]`);
        if (activeBtn) activeBtn.classList.add("active");
        renderExercises(currentPlan.days[day].exercises);
    }

    function saveCurrentDayExercises() {
        const rows = exercisesContainer.querySelectorAll(".tr-plan-ex-row");
        currentPlan.days[activeDay].exercises = [...rows].map(row => ({
            exercise: {
                id: row.dataset.id,
                name: row.querySelector(".tr-plan-ex-name").textContent
            },
            sets: parseInt(row.querySelector(".ex-sets").value) || 3,
            reps: row.querySelector(".ex-reps").value || "8-12",
            load: parseFloat(row.querySelector(".ex-load").value) || 0
        }));
    }

    function renderExercises(list) {
        exercisesContainer.innerHTML = "";

        list.forEach(item => {
            const row = document.createElement("div");
            row.className = "tr-plan-ex-row";
            row.dataset.id = item.exercise.id;
            row.draggable = true;

            row.innerHTML = `
                <div class="tr-plan-ex-name">${item.exercise.name}</div>
                <div class="tr-plan-ex-inputs">
                    <div class="tr-plan-field">
                        <div class="tr-plan-label">Підхід</div>
                        <div class="tr-plan-input-box">
                            <input class="ex-sets" type="number" min="1" value="${item.sets ?? 3}">
                            <div class="tr-plan-arrows">
                                <div class="tr-plan-arrow" data-type="sets" data-dir="inc">▲</div>
                                <div class="tr-plan-arrow" data-type="sets" data-dir="dec">▼</div>
                            </div>
                        </div>
                    </div>
                    <div class="tr-plan-field">
                        <div class="tr-plan-label">Повторення</div>
                        <div class="tr-plan-input-box">
                            <input class="ex-reps" type="text" value="${item.reps ?? "8-12"}">
                        </div>
                    </div>
                    <div class="tr-plan-field">
                        <div class="tr-plan-label">Вага</div>
                        <div class="tr-plan-input-box">
                            <input class="ex-load" type="number" min="0" step="0.5" value="${item.load ?? 0}">
                            <div class="tr-plan-arrows">
                                <div class="tr-plan-arrow" data-type="load" data-dir="inc">▲</div>
                                <div class="tr-plan-arrow" data-type="load" data-dir="dec">▼</div>
                            </div>
                        </div>
                    </div>
                    <button class="tr-plan-ex-remove">&times;</button>
                </div>
            `;

            row.querySelector(".tr-plan-ex-remove").onclick = () => {
                currentPlan.days[activeDay].exercises =
                    currentPlan.days[activeDay].exercises.filter(ex => ex.exercise.id !== item.exercise.id);
                renderExercises(currentPlan.days[activeDay].exercises);
            };

            row.querySelectorAll(".tr-plan-arrow").forEach(btn => {
                const type = btn.dataset.type;
                const dir = btn.dataset.dir;
                const input = btn.closest(".tr-plan-input-box").querySelector("input");

                btn.onclick = () => {
                    let val = parseFloat(input.value) || 0;
                    if (type === "sets") {
                        val = dir === "inc" ? val + 1 : Math.max(1, val - 1);
                    } else if (type === "load") {
                        val = dir === "inc" ? val + 0.5 : Math.max(0, val - 0.5);
                    }
                    input.value = val;
                };
            });

            row.addEventListener("dragstart", () => row.classList.add("dragging"));
            row.addEventListener("dragend", () => row.classList.remove("dragging"));

            exercisesContainer.appendChild(row);
        });

        exercisesContainer.ondragover = e => {
            e.preventDefault();
            const dragging = exercisesContainer.querySelector(".dragging");
            if (!dragging) return;
            const after = [...exercisesContainer.querySelectorAll(".tr-plan-ex-row:not(.dragging)")]
                .find(r => e.clientY <= r.getBoundingClientRect().top + r.offsetHeight / 2);
            if (after) exercisesContainer.insertBefore(dragging, after);
            else exercisesContainer.appendChild(dragging);
        };
    }

    addExerciseBtn.onclick = () => {
        openExercisePicker(ex => {
            currentPlan.days[activeDay].exercises.push({
                exercise: ex,
                sets: 3,
                reps: "8-12",
                load: 0
            });
            renderExercises(currentPlan.days[activeDay].exercises);
        });
    };

    function save() {
        saveCurrentDayExercises();
        ensureStructure();

        const payload = {
            name: currentPlan.name,
            days: {}
        };

        daysOrder.forEach(k => {
            payload.days[k] = currentPlan.days[k].exercises.map(item => ({
                exercise: { id: item.exercise.id },
                sets: item.sets ?? 3,
                reps: item.reps ?? "8-12",
                load: item.load ?? 0
            }));
        });

        payload.is_active = true;

        const text = saveBtn.querySelector(".btn-text");
        const loader = saveBtn.querySelector(".btn-loader");
        text.classList.add("hidden");
        loader.classList.remove("hidden");

        TrainingAPI.savePlan(payload)
            .then(() => {
                loader.classList.add("hidden");
                text.classList.remove("hidden");
                if (window.refreshPlanData) {
                    window.refreshPlanData();
                }
                close();
            })
            .catch(() => {
                loader.classList.add("hidden");
                text.classList.remove("hidden");
            });
    }

    function bind() {
        saveBtn.onclick = save;
        closeBtns.forEach(btn => btn.onclick = close);
        const editBtn = document.getElementById("tr-edit-plan");
        if (editBtn) editBtn.onclick = () => open();
    }

    function init() {
        bind();
    }

    return { init };
})();

document.addEventListener("DOMContentLoaded", () => {
    PlanModal.init();
});

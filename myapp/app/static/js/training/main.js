function renderCurrentDate() {
    const el = document.getElementById("current-date");
    if (!el) return;

    const d = new Date();
    el.textContent = d.toLocaleDateString("uk-UA", {
        weekday: "long",
        day: "numeric",
        month: "long"
    });
}

function renderAnalytics(data) {
    const map = {
        "tr-performance": data.performance,
        "tr-recovery": data.recovery,
        "tr-strength": data.strength,
        "tr-endurance": data.endurance,
        "tr-mobility": data.mobility,
        "tr-fatigue": data.fatigue
    };

    Object.entries(map).forEach(([id, val]) => {
        const el = document.getElementById(id);
        if (el) el.textContent = val != null ? Math.round(val) : "—";
    });
}

function renderStrengthTestResults(perf) {
    if (!perf) return;

    const p = document.getElementById("st-result-pushups");
    const s = document.getElementById("st-result-squats");
    const si = document.getElementById("st-result-situps");

    if (p) p.textContent = perf.pushups ?? "—";
    if (s) s.textContent = perf.squats ?? "—";
    if (si) si.textContent = perf.situps ?? "—";
}

function renderRecommendations(data) {
    const weak = document.getElementById("tr-weak-points");
    const ex = document.getElementById("tr-exercise-recommendations");
    const rec = document.getElementById("tr-recovery-recommendations");
    const nut = document.getElementById("tr-nutrition-recommendations");

    const safeArr = v => Array.isArray(v) ? v : (v ? [v] : []);

    if (weak) {
        weak.innerHTML = "";
        safeArr(data.weak_points).forEach(w => {
            const li = document.createElement("li");
            li.textContent = w;
            weak.appendChild(li);
        });
    }

    if (ex) {
        ex.innerHTML = "";
        safeArr(data.exercise_recommendations).forEach(r => {
            const li = document.createElement("li");
            li.textContent = r;
            ex.appendChild(li);
        });
    }

    if (rec) {
        rec.innerHTML = "";
        safeArr(data.recovery).forEach(r => {
            const li = document.createElement("li");
            li.textContent = r;
            rec.appendChild(li);
        });
    }

    if (nut) {
        nut.innerHTML = "";
        safeArr(data.nutrition).forEach(r => {
            const li = document.createElement("li");
            li.textContent = r;
            nut.appendChild(li);
        });
    }
}

let allExercises = [];
let currentPlan = { name: "Мій план", days: {} };
let currentWorkout = [];

const daysOrder = ["mon", "tue", "wed", "thu", "fri", "sat", "sun"];

function ensurePlanStructure() {
    if (!currentPlan.days) currentPlan.days = {};

    daysOrder.forEach(k => {
        if (!currentPlan.days[k]) {
            currentPlan.days[k] = { exercises: [] };
        }
    });
}

function getTodayKey() {
    return ["sun", "mon", "tue", "wed", "thu", "fri", "sat"][new Date().getDay()];
}

function loadPlan() {
    TrainingAPI.getPlans()
        .then(plans => {
            if (!plans.length) {
                currentPlan = { name: "Мій план", days: {} };
            } else {
                const active = plans.find(p => p.is_active) || plans[0];
                currentPlan = {
                    name: active.name || "Мій план",
                    days: active.days || {}
                };
            }

            ensurePlanStructure();
            syncWorkoutWithPlanToday();
        })
        .catch(() => {
            currentPlan = { name: "Мій план", days: {} };
            ensurePlanStructure();
            syncWorkoutWithPlanToday();
        });
}

function syncWorkoutWithPlanToday() {
    const dayKey = getTodayKey();
    const day = currentPlan.days[dayKey] || { exercises: [] };

    currentWorkout = [];

    day.exercises.forEach(item => {
        const exObj = allExercises.find(e => e.id === item.exercise.id);
        if (!exObj) return;

        currentWorkout.push({
            exercise: exObj,
            sets: item.sets ?? 3,
            reps: item.reps ?? "8-12",
            load: item.load ?? 0,
            done: false
        });
    });

    renderWorkoutList();
}


function openExercisePicker(callback) {
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

    renderList(allExercises);

    if (search) {
        search.value = "";
        search.oninput = () => {
            const q = search.value.trim().toLowerCase();
            if (!q) renderList(allExercises);
            else renderList(allExercises.filter(ex => ex.name.toLowerCase().includes(q)));
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

window.refreshPlanData = function() {
    loadPlan();
};

document.addEventListener("DOMContentLoaded", () => {
    renderCurrentDate();

    TrainingAPI.getExercises().then(data => {
        allExercises = data.items || data || [];
        loadPlan();
    });

    TrainingAPI.getAnalytics().then(data => {
        renderAnalytics(data);
        const perf = data.raw_performance || data.performance_raw || data;
        renderStrengthTestResults(perf);
    });

    TrainingAPI.getRecommendations().then(renderRecommendations);

    const addExercise = document.getElementById("tr-add-exercise");
    if (addExercise) {
        addExercise.onclick = () => {
            openExercisePicker(ex => {
                currentWorkout.push({
                    exercise: ex,
                    sets: 3,
                    reps: "8-12",
                    load: 0,
                    done: false
                });
                renderWorkoutList();
            });
        };
    }

    const saveWorkout = document.getElementById("tr-save-workout");
    if (saveWorkout) {
        saveWorkout.onclick = () => {
            if (!currentWorkout.length) return;

            const titleInput = document.getElementById("tr-workout-title");
            const title = titleInput ? titleInput.value.trim() : "";

            const payloadExercises = currentWorkout.map(item => ({
                exercise: { id: item.exercise.id },
                sets: item.sets ?? 3,
                reps: item.reps ?? "8-12",
                load: item.load ?? 0
            }));

            const btn = saveWorkout;
            btn.disabled = true;

            TrainingAPI.completeSession({
                title,
                exercises: payloadExercises
            }).then(() => {
                currentWorkout = [];
                if (titleInput) titleInput.value = "";
                renderWorkoutList();
                TrainingAPI.getHeatmap().then(() => {});
                loadPlan();
            }).finally(() => {
                btn.disabled = false;
            });
        };
    }

    renderWorkoutList();
});

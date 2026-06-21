document.addEventListener("DOMContentLoaded", () => {
    setTodayDate();
    loadAnalytics();
    loadPlan();
    loadTodaySession();
    loadRecommendations();
    setupButtons();
});

function setTodayDate() {
    const el = document.getElementById("current-date");
    const d = new Date();
    const opts = { day: "2-digit", month: "2-digit", year: "numeric" };
    el.textContent = d.toLocaleDateString("uk-UA", opts);
}

function setupButtons() {
    document.getElementById("tr-start-session").addEventListener("click", () => {
        openModal("modal-start-session");
    });

    document.getElementById("tr-add-exercise").addEventListener("click", () => {
        openModal("modal-add-exercise");
        loadExerciseFilters();
        loadExerciseSearch();
    });

    document.getElementById("tr-finish-session").addEventListener("click", () => {
        openModal("modal-finish-session");
    });
}

async function loadAnalytics() {
    try {
        const res = await fetch("/api/training/analytics");
        const data = await res.json();

        document.getElementById("tr-performance").textContent = data.performance || "—";
        document.getElementById("tr-recovery").textContent = data.recovery || "—";
    } catch (e) {
        console.error("Analytics error:", e);
    }
}

async function loadPlan() {
    try {
        const res = await fetch("/api/training/plan");
        const data = await res.json();

        const info = document.getElementById("tr-plan-info");
        info.innerHTML = `
            <div class="plan-name">${data.name}</div>
            <div class="plan-meta">${data.type} · ${data.duration} хв</div>
        `;

        const days = document.getElementById("tr-plan-days");
        days.innerHTML = "";

        (data.meta.days || []).forEach((d, i) => {
            const el = document.createElement("div");
            el.className = "plan-day";
            el.innerHTML = `
                <div class="plan-day-title">День ${i + 1}</div>
                <div class="plan-day-exercises">${d.exercises.length} вправ</div>
            `;
            days.appendChild(el);
        });

    } catch (e) {
        console.error("Plan error:", e);
    }
}

async function loadTodaySession() {
    try {
        const res = await fetch("/api/training/today");
        const data = await res.json();

        document.getElementById("tr-session-title").textContent = data.title || "Немає активної сесії";
        document.getElementById("tr-session-type").textContent = data.sessionId || "—";

        renderMuscleBalance(data.muscles);
        renderHints(data.hints || []);
        renderSessionExercises(data.exercises || []);

    } catch (e) {
        console.error("Today session error:", e);
    }
}

function renderMuscleBalance(muscles) {
    const list = document.getElementById("tr-muscle-balance");
    list.innerHTML = "";

    Object.entries(muscles).forEach(([slug, pct]) => {
        const li = document.createElement("li");
        li.innerHTML = `
            <span class="muscle-name">${slug}</span>
            <span class="muscle-value">${Math.round(pct * 100)}%</span>
        `;
        list.appendChild(li);
    });
}

function renderHints(hints) {
    const list = document.getElementById("tr-hints-list");
    list.innerHTML = "";

    hints.forEach(h => {
        const li = document.createElement("li");
        li.textContent = h;
        list.appendChild(li);
    });
}

function renderSessionExercises(exercises) {
    const list = document.getElementById("tr-exercise-list");
    list.innerHTML = "";

    exercises.forEach(ex => {
        const el = document.createElement("div");
        el.className = "session-exercise";
        el.innerHTML = `
            <div class="session-ex-name">${ex.name}</div>
            <div class="session-ex-meta">${ex.reps || "8"} повторень · ${ex.sets || 3} підходи</div>
        `;
        list.appendChild(el);
    });
}

async function loadRecommendations() {
    try {
        const res = await fetch("/api/training/recommendations");
        const data = await res.json();

        fillList("tr-weak-points", data.weak_points);
        fillList("tr-exercise-recommendations", data.exercise_recommendations);
        fillList("tr-recovery-recommendations", data.recovery);
        fillList("tr-nutrition-recommendations", data.nutrition);

    } catch (e) {
        console.error("Recommendations error:", e);
    }
}

function fillList(id, arr) {
    const list = document.getElementById(id);
    list.innerHTML = "";
    arr.forEach(x => {
        const li = document.createElement("li");
        li.textContent = x;
        list.appendChild(li);
    });
}

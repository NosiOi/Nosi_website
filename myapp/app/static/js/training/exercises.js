async function loadExerciseFilters() {
    const muscles = await fetch("/api/muscles").then(r => r.json());
    const equipment = await fetch("/api/equipment").then(r => r.json());

    const msel = document.getElementById("ex-muscle-filter");
    const esel = document.getElementById("ex-equipment-filter");

    msel.innerHTML = `<option value="">М’язи</option>`;
    esel.innerHTML = `<option value="">Обладнання</option>`;

    muscles.forEach(m => msel.innerHTML += `<option value="${m.slug}">${m.name}</option>`);
    equipment.forEach(e => esel.innerHTML += `<option value="${e.name}">${e.name}</option>`);
}

async function loadExerciseSearch() {
    const q = document.getElementById("ex-search").value;
    const muscle = document.getElementById("ex-muscle-filter").value;
    const equipment = document.getElementById("ex-equipment-filter").value;

    const params = new URLSearchParams();
    if (q) params.append("q", q);
    if (muscle) params.append("muscle", muscle);
    if (equipment) params.append("equipment", equipment);

    const res = await fetch(`/api/exercises?${params.toString()}`);
    const data = await res.json();

    const list = document.getElementById("ex-search-results");
    list.innerHTML = "";

    data.items.forEach(ex => {
        const el = document.createElement("div");
        el.className = "exercise-item";
        el.innerHTML = `
            <div class="exercise-name">${ex.name}</div>
            <button class="btn primary" data-id="${ex.id}">Додати</button>
        `;
        el.querySelector("button").addEventListener("click", () => addExerciseToSession(ex.id));
        list.appendChild(el);
    });
}

async function addExerciseToSession(id) {
    const sessionType = document.getElementById("tr-session-type").textContent;
    if (!sessionType.startsWith("plan-") && sessionType !== "fallback") return;

    const sid = sessionType.replace("plan-", "");

    await fetch(`/api/session/${sid}/exercises`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ exercise_id: id })
    });

    closeModal("modal-add-exercise");
    loadTodaySession();
}

document.getElementById("ex-search").addEventListener("input", loadExerciseSearch);
document.getElementById("ex-muscle-filter").addEventListener("change", loadExerciseSearch);
document.getElementById("ex-equipment-filter").addEventListener("change", loadExerciseSearch);

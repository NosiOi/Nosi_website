import { trainingStore } from "./store.js";

export function renderWorkoutList() {
    const list = document.getElementById("tr-workout-exercise-list");
    if (!list) return;

    list.innerHTML = "";

    if (!trainingStore.workout.length) {
        const empty = document.createElement("div");
        empty.className = "tr-plan-day-empty";
        empty.textContent = "Додай вправи у тренування";
        list.appendChild(empty);
        return;
    }

    const sorted = [...trainingStore.workout].sort((a, b) => {
        return (a.done ? 1 : 0) - (b.done ? 1 : 0);
    });

    sorted.forEach(item => {
        const idx = trainingStore.workout.indexOf(item);

        const row = document.createElement("div");
        row.className = "tr-session-ex-row";
        if (item.done) row.classList.add("tr-ex-done");

        const left = document.createElement("div");
        left.className = "tr-session-ex-left";

        const name = document.createElement("div");
        name.className = "tr-session-ex-name";
        name.textContent = item.exercise.name;

        const inputs = document.createElement("div");
        inputs.className = "tr-session-ex-inputs";

        const setsBox = document.createElement("input");
        setsBox.type = "number";
        setsBox.min = "1";
        setsBox.value = item.sets;
        setsBox.className = "tr-ex-sets";
        setsBox.oninput = () => {
            if (!item.done) item.sets = parseInt(setsBox.value) || 1;
        };

        const repsBox = document.createElement("input");
        repsBox.type = "text";
        repsBox.value = item.reps;
        repsBox.className = "tr-ex-reps";
        repsBox.oninput = () => {
            if (!item.done) item.reps = repsBox.value || "8-12";
        };

        const loadBox = document.createElement("input");
        loadBox.type = "number";
        loadBox.min = "0";
        loadBox.step = "0.5";
        loadBox.value = item.load;
        loadBox.className = "tr-ex-load";
        loadBox.oninput = () => {
            if (!item.done) item.load = parseFloat(loadBox.value) || 0;
        };

        inputs.append(setsBox, repsBox, loadBox);
        left.append(name, inputs);

        const right = document.createElement("div");
        right.className = "tr-session-ex-right";

        const doneBox = document.createElement("div");
        doneBox.className = "tr-ex-check";
        if (item.done) doneBox.classList.add("checked");
        doneBox.onclick = () => {
            item.done = !item.done;
            renderWorkoutList();
        };

        const del = document.createElement("button");
        del.className = "tr-btn tr-btn-danger";
        del.textContent = "×";
        del.onclick = () => {
            trainingStore.workout.splice(idx, 1);
            renderWorkoutList();
        };

        right.append(doneBox, del);
        row.append(left, right);
        list.appendChild(row);
    });
}

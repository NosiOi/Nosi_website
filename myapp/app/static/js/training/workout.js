import { trainingStore } from "./store.js";

export function renderWorkoutList() {
    const box = document.getElementById("tr-workout-exercise-list");
    if (!box) return;
    box.innerHTML = "";

    const sorted = [...trainingStore.workout].sort((a, b) => {
        if (a.done && !b.done) return 1;
        if (!a.done && b.done) return -1;
        return 0;
    });

    sorted.forEach(item => {
        const row = document.createElement("div");
        row.className = "tr-session-ex-row";
        if (item.done) row.classList.add("tr-ex-done");

        const name = document.createElement("div");
        name.className = "tr-session-ex-name";
        name.textContent = item.exercise.name;

        const inputs = document.createElement("div");
        inputs.className = "tr-session-ex-inputs";

        const makeInlineBlock = (labelText, initialValue, onChange, isRange = false) => {
            const wrap = document.createElement("div");
            wrap.className = "tr-input-inline";

            const input = document.createElement("input");
            input.className = "tr-input-field";
            input.value = initialValue;
            input.oninput = () => onChange(input.value);

            const arrows = document.createElement("div");
            arrows.className = "tr-input-arrows";

            const up = document.createElement("div");
            up.className = "tr-arrow tr-arrow-up";
            up.onclick = () => {
                const val = input.value;
                if (isRange) {
                    const [a, b] = val.split("-").map(Number);
                    const nv = `${a + 1}-${b + 1}`;
                    input.value = nv;
                    onChange(nv);
                } else {
                    const nv = (parseInt(val, 10) || 0) + 1;
                    input.value = nv;
                    onChange(nv);
                }
            };

            const down = document.createElement("div");
            down.className = "tr-arrow tr-arrow-down";
            down.onclick = () => {
                const val = input.value;
                if (isRange) {
                    const [a, b] = val.split("-").map(Number);
                    const na = Math.max(1, a - 1);
                    const nb = Math.max(na, b - 1);
                    const nv = `${na}-${nb}`;
                    input.value = nv;
                    onChange(nv);
                } else {
                    const nv = Math.max(0, (parseInt(val, 10) || 0) - 1);
                    input.value = nv;
                    onChange(nv);
                }
            };

            const label = document.createElement("span");
            label.className = "tr-input-inline-label";
            label.textContent = labelText;

            arrows.appendChild(up);
            arrows.appendChild(down);
            wrap.appendChild(input);
            wrap.appendChild(arrows);
            wrap.appendChild(label);

            return wrap;
        };

        const setsBlock = makeInlineBlock("підх.", item.sets, v => item.sets = parseInt(v, 10) || 0);
        const repsBlock = makeInlineBlock("повт.", item.reps, v => item.reps = v, true);
        const loadBlock = makeInlineBlock("кг", item.load, v => item.load = parseFloat(v) || 0);

        inputs.appendChild(setsBlock);
        inputs.appendChild(repsBlock);
        inputs.appendChild(loadBlock);

        const check = document.createElement("div");
        check.className = "tr-ex-check";
        if (item.done) check.classList.add("checked");
        check.onclick = () => {
            item.done = !item.done;
            renderWorkoutList();
        };

        row.appendChild(name);
        row.appendChild(inputs);
        row.appendChild(check);

        box.appendChild(row);
    });
}

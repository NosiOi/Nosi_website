import { createCounterField, createRepsField } from "./counters.js";
import { enableDrag } from "../interactions/dragdrop.js";

export function createExerciseCard(ex, index, list, rerender, openPicker) {
    const card = document.createElement("div");
    card.className = "tr-plan-card";

    card.innerHTML = `
        <div class="tr-plan-card-header">
            <div class="tr-plan-card-header-left">
                <div class="tr-plan-card-strip"></div>
                <button class="tr-plan-ex-name">${ex.exercise.name}</button>
            </div>
            <div class="tr-plan-card-header-right">
                <button class="tr-plan-card-drag">
                    <svg width="18" height="18">
                        <circle cx="9" cy="12" r="1"/>
                        <circle cx="9" cy="5" r="1"/>
                        <circle cx="9" cy="19" r="1"/>
                        <circle cx="15" cy="12" r="1"/>
                        <circle cx="15" cy="5" r="1"/>
                        <circle cx="15" cy="19" r="1"/>
                    </svg>
                </button>
                <button class="tr-plan-card-delete">
                    <svg width="18" height="18">
                        <path d="M10 11v6"/>
                        <path d="M14 11v6"/>
                        <path d="M19 6v14a2 2 0 0 1-2 2H7a2 2 0 0 1-2-2V6"/>
                        <path d="M3 6h18"/>
                        <path d="M8 6V4a2 2 0 0 1 2-2h4a2 2 0 0 1 2 2v2"/>
                    </svg>
                </button>
            </div>
        </div>
        <div class="tr-plan-card-body"></div>
    `;

    const nameBtn = card.querySelector(".tr-plan-ex-name");
    const deleteBtn = card.querySelector(".tr-plan-card-delete");
    const body = card.querySelector(".tr-plan-card-body");

    const reps = createRepsField(ex.reps, v => ex.reps = v);
    const sets = createCounterField("Підходи", `<svg width="18" height="18"></svg>`, ex.sets, v => ex.sets = v);
    const load = createCounterField("Вага (кг)", `<svg width="18" height="18"></svg>`, ex.load, v => ex.load = v);

    body.appendChild(reps);
    body.appendChild(sets);
    body.appendChild(load);

    nameBtn.onclick = () => openPicker(ex, rerender);

    deleteBtn.onclick = () => {
        list.splice(index, 1);
        rerender();
    };

    enableDrag(card, index, list, rerender);

    return card;
}

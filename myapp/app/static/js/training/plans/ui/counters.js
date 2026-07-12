export function createCounterField(label, iconSvg, value, onChange) {
    const field = document.createElement("div");
    field.className = "tr-plan-field";

    field.innerHTML = `
        <div class="tr-plan-field-label-row">
            <span class="tr-plan-field-icon">${iconSvg}</span>
            <span class="tr-plan-field-label">${label}</span>
        </div>
        <div class="tr-plan-counter">
            <button class="tr-plan-counter-btn tr-plan-counter-minus">−</button>
            <input type="number" class="tr-plan-counter-input" value="${value}">
            <button class="tr-plan-counter-btn tr-plan-counter-plus">+</button>
        </div>
    `;

    const minus = field.querySelector(".tr-plan-counter-minus");
    const plus = field.querySelector(".tr-plan-counter-plus");
    const input = field.querySelector(".tr-plan-counter-input");

    minus.onclick = () => {
        const val = Number(input.value);
        if (Number.isNaN(val)) return;
        const next = Math.max(0, val - 1);
        input.value = next;
        onChange(next);
    };

    plus.onclick = () => {
        const val = Number(input.value);
        if (Number.isNaN(val)) return;
        const next = val + 1;
        input.value = next;
        onChange(next);
    };

    input.oninput = () => {
        const val = Number(input.value);
        if (Number.isNaN(val)) return;
        onChange(val);
    };

    return field;
}

export function createRepsField(value, onChange) {
    const field = document.createElement("div");
    field.className = "tr-plan-field";

    field.innerHTML = `
        <div class="tr-plan-field-label-row">
            <span class="tr-plan-field-icon"><svg width="18" height="18"></svg></span>
            <span class="tr-plan-field-label">Повтори</span>
        </div>
        <div class="tr-plan-counter">
            <button class="tr-plan-counter-btn tr-plan-counter-minus">−</button>
            <input type="text" class="tr-plan-counter-input tr-plan-reps-input" value="${value}" placeholder="Наприклад: 10 або 8–12">
            <button class="tr-plan-counter-btn tr-plan-counter-plus">+</button>
        </div>
    `;

    const minus = field.querySelector(".tr-plan-counter-minus");
    const plus = field.querySelector(".tr-plan-counter-plus");
    const input = field.querySelector(".tr-plan-reps-input");

    minus.onclick = () => {
        const num = Number(input.value);
        if (Number.isNaN(num)) return;
        const next = Math.max(0, num - 1);
        input.value = next;
        onChange(next);
    };

    plus.onclick = () => {
        const num = Number(input.value);
        if (Number.isNaN(num)) return;
        const next = num + 1;
        input.value = next;
        onChange(next);
    };

    input.oninput = () => onChange(input.value);

    return field;
}

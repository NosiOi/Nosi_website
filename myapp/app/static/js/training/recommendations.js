const safeArr = v => Array.isArray(v) ? v : (v ? [v] : []);

export function renderRecommendations(data) {
    renderWeakPoints(data.muscles || {});
    renderRecommendedExercises(data.recommended_exercises || []);
    renderBalance(data.muscles || {});
}

function renderWeakPoints(muscles) {
    const box = document.getElementById("tr-weak-points");
    if (!box) return;
    box.innerHTML = "";
    safeArr(muscles.weak).slice(0, 5).forEach(m => {
        const badge = document.createElement("span");
        badge.className = "tr-rec-badge";
        badge.textContent = m;
        box.appendChild(badge);
    });
}

function mapReasonText(r) {
    const t = String(r).toLowerCase();
    if (t.includes("weak muscle group")) return "Покращує слабкі м’язи";
    if (t.includes("weak movement pattern")) return "Покращує техніку руху";
    if (t.includes("mobility")) return "Покращує мобільність";
    return r;
}

function renderRecommendedExercises(list) {
    const col1 = document.getElementById("tr-exercise-col-1");
    const col2 = document.getElementById("tr-exercise-col-2");

    if (!col1 || !col2) return;

    col1.innerHTML = "";
    col2.innerHTML = "";

    const items = safeArr(list).slice(0, 4);

    items.forEach((item, i) => {
        const wrap = document.createElement("div");
        wrap.className = "tr-rec-exercise";

        const title = document.createElement("div");
        title.className = "tr-rec-ex-title";
        title.textContent = item.exercise;

        const desc = document.createElement("div");
        desc.className = "tr-rec-ex-desc";
        const firstReason = safeArr(item.reasons)[0] || "";
        desc.textContent = mapReasonText(firstReason);

        wrap.appendChild(title);
        wrap.appendChild(desc);

        if (i < 2) col1.appendChild(wrap);
        else col2.appendChild(wrap);
    });
}

function renderBalance(muscles) {
    const balancedBox = document.getElementById("tr-balance-balanced");
    const overloadedBox = document.getElementById("tr-balance-overloaded");

    if (!balancedBox || !overloadedBox) return;

    balancedBox.innerHTML = "";
    overloadedBox.innerHTML = "";

    safeArr(muscles.balanced).slice(0, 3).forEach(m => {
        const row = document.createElement("div");
        row.className = "tr-balance-item";
        row.innerHTML = `<span>${m}</span><span>🟢 Збалансовані</span>`;
        balancedBox.appendChild(row);
    });

    safeArr(muscles.overloaded).slice(0, 3).forEach(m => {
        const row = document.createElement("div");
        row.className = "tr-balance-item";
        row.innerHTML = `<span>${m}</span><span>🔴 Перевантажені</span>`;
        overloadedBox.appendChild(row);
    });
}

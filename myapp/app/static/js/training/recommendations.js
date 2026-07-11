const safeArr = v => Array.isArray(v) ? v : (v ? [v] : []);

function loadRecommendations() {
    fetch("/api/training/recommendations")
        .then(r => r.json())
        .then(data => renderRecommendationsBlock(data))
        .catch(() => console.error("Failed to load recommendations"));
}

function renderRecommendationsBlock(data) {
    renderRecommendedExercises(data.recommended_exercises);
    renderMuscleSummary(data.muscles);
    renderPatternSummary(data.patterns);
    renderRecoverySummary(data.recovery);
    renderLoadSummary(data.load);
    renderDiversitySummary(data.diversity);
    renderFrequencySummary(data.frequency);
}

function renderRecommendedExercises(list) {
    const box = document.getElementById("rec-exercises");
    if (!box) return;

    box.innerHTML = "";

    safeArr(list).forEach(item => {
        const div = document.createElement("div");
        div.className = "rec-item";

        const name = document.createElement("div");
        name.className = "rec-name";
        name.textContent = item.exercise;

        const score = document.createElement("div");
        score.className = "rec-score";
        score.textContent = item.score;

        const reasons = document.createElement("ul");
        reasons.className = "rec-reasons";
        safeArr(item.reasons).forEach(r => {
            const li = document.createElement("li");
            li.textContent = r;
            reasons.appendChild(li);
        });

        div.append(name, score, reasons);
        box.appendChild(div);
    });
}

function renderMuscleSummary(muscles) {
    const box = document.getElementById("rec-muscles");
    if (!box) return;

    box.innerHTML = "";

    safeArr(muscles.details).forEach(m => {
        const li = document.createElement("li");
        li.textContent = `${m.muscle}: ${m.score.toFixed(2)}`;
        box.appendChild(li);
    });
}

function renderPatternSummary(patterns) {
    const box = document.getElementById("rec-patterns");
    if (!box) return;

    box.innerHTML = "";

    safeArr(patterns.details).forEach(p => {
        const li = document.createElement("li");
        li.textContent = `${p.pattern}: ${p.score.toFixed(2)}`;
        box.appendChild(li);
    });
}

function renderRecoverySummary(recovery) {
    const box = document.getElementById("rec-recovery");
    if (!box) return;

    box.innerHTML = `
        <li>Sleep: ${recovery.sleep}</li>
        <li>Stress: ${recovery.stress}</li>
        <li>Soreness: ${recovery.soreness}</li>
        <li>Hydration: ${recovery.hydration}</li>
    `;
}

function renderLoadSummary(load) {
    const box = document.getElementById("rec-load");
    if (!box) return;

    box.innerHTML = `
        <li>Total load: ${load.total_load.toFixed(1)}</li>
        <li>Average load: ${load.avg_load.toFixed(1)}</li>
        <li>Peak load: ${load.peak_load.toFixed(1)}</li>
    `;
}

function renderDiversitySummary(div) {
    const box = document.getElementById("rec-diversity");
    if (!box) return;

    box.innerHTML = `
        <li>Status: ${div.status}</li>
        <li>Score: ${div.score.toFixed(2)}</li>
        <li>Unique exercises: ${div.unique_exercises}</li>
        <li>Total exercises: ${div.total_exercises}</li>
    `;
}

function renderFrequencySummary(freq) {
    const box = document.getElementById("rec-frequency");
    if (!box) return;

    box.innerHTML = `
        <li>Total: ${freq.total}</li>
        <li>Unique: ${freq.unique}</li>
    `;
}

document.addEventListener("DOMContentLoaded", () => {
    loadRecommendations();
});

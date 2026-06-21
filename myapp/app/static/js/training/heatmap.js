document.addEventListener("DOMContentLoaded", () => {
    const yearSelect = document.getElementById("tr-heatmap-year");
    if (!yearSelect) return;

    yearSelect.addEventListener("change", () => {
        loadTrainingHeatmap(yearSelect.value);
    });

    loadTrainingHeatmap(yearSelect.value);
});

async function loadTrainingHeatmap(year) {
    try {
        const res = await fetch(`/api/training/heatmap?year=${year}`);
        const data = await res.json();
        renderTrainingHeatmap(data.days || []);
    } catch (e) {
        console.error("Heatmap load error:", e);
    }
}

function renderTrainingHeatmap(days) {
    const grid = document.getElementById("tr-heatmap-grid");
    if (!grid) return;

    grid.innerHTML = "";

    days.forEach((d) => {
        const cell = document.createElement("div");
        cell.className = "tr-heatmap-cell";
        cell.dataset.level = d.level;

        if (d.is_today) cell.classList.add("today");

        const tooltip = document.createElement("div");
        tooltip.className = "tr-heatmap-tooltip";
        tooltip.textContent = `${d.load}% навантаження`;

        cell.appendChild(tooltip);
        grid.appendChild(cell);
    });
}

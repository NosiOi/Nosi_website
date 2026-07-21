export function renderHeatmapWidget(heatmap) {
    const el = document.getElementById("heatmap-widget");
    if (!el) return;

    if (!heatmap || !Array.isArray(heatmap) || heatmap.length === 0) {
        el.innerHTML = `<div class="empty">Немає історії відновлення</div>`;
        return;
    }

    // TODO: render calendar heatmap instead of simple summary
    el.innerHTML = `
        <div class="heatmap-card">
            <h3>Історія відновлення</h3>
            <p>Днів у вибірці: <strong>${heatmap.length}</strong></p>
        </div>
    `;
}

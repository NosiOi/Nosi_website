export function renderHeatmapWidget(heatmap) {
    const el = document.getElementById("heatmap-widget");
    if (!el) return;

    if (!heatmap || heatmap.length === 0) {
        el.innerHTML = `<div class="empty">Немає історії відновлення</div>`;
        return;
    }

    el.innerHTML = `
        <div class="heatmap-card">
            <h3>Історія відновлення</h3>
            <p>Днів: ${heatmap.length}</p>
        </div>
    `;
}

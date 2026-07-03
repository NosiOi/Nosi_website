const TrainingExercises = (() => {
    function loadExercisesList(containerId) {
        const container = document.getElementById(containerId);
        if (!container) return;
        TrainingAPI.getExercises()
            .then(data => {
                const items = data.items || data || [];
                container.innerHTML = "";
                items.forEach(ex => {
                    const row = document.createElement("div");
                    row.className = "tr-exercise-row";
                    const name = document.createElement("div");
                    name.className = "tr-exercise-name";
                    name.textContent = ex.name;
                    const meta = document.createElement("div");
                    meta.className = "tr-exercise-meta";
                    meta.textContent = (ex.muscles_primary || []).join(", ");
                    row.appendChild(name);
                    row.appendChild(meta);
                    container.appendChild(row);
                });
            })
            .catch(() => {});
    }
    return { loadExercisesList };
})();

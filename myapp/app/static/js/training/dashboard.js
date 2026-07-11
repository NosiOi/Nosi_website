import { trainingStore } from "./store.js";

export function renderCurrentDate() {
    const el = document.getElementById("current-date");
    if (!el) return;
    const d = new Date();
    el.textContent = d.toLocaleDateString("uk-UA", {
        weekday: "long",
        day: "numeric",
        month: "long"
    });
}

export function renderAnalytics(data) {
    const map = {
        "tr-performance": data.performance,
        "tr-recovery": data.recovery,
        "tr-strength": data.strength,
        "tr-endurance": data.endurance,
        "tr-mobility": data.mobility,
        "tr-fatigue": data.fatigue
    };
    Object.entries(map).forEach(([id, val]) => {
        const el = document.getElementById(id);
        if (el) el.textContent = val != null ? Math.round(val) : "—";
    });
}

export function renderStrengthTestResults(perf) {
    if (!perf) return;
    const p = document.getElementById("st-result-pushups");
    const s = document.getElementById("st-result-squats");
    const si = document.getElementById("st-result-situps");
    if (p) p.textContent = perf.pushups ?? "—";
    if (s) s.textContent = perf.squats ?? "—";
    if (si) si.textContent = perf.situps ?? "—";
}

import { trainingStore } from "./store.js";
import { renderWorkoutList } from "./workout.js";

export function ensurePlanStructure() {
    if (!trainingStore.plan.days) trainingStore.plan.days = {};
    ["mon","tue","wed","thu","fri","sat","sun"].forEach(k => {
        if (!trainingStore.plan.days[k]) {
            trainingStore.plan.days[k] = { exercises: [] };
        }
    });
}

export function getTodayKey() {
    return ["sun","mon","tue","wed","thu","fri","sat"][new Date().getDay()];
}

export async function loadPlan() {
    try {
        const plans = await TrainingAPI.getPlans();
        if (!plans.length) {
            trainingStore.plan = { name: "Мій план", days: {} };
        } else {
            const active = plans.find(p => p.is_active) || plans[0];
            trainingStore.plan = {
                name: active.name || "Мій план",
                days: active.days || {}
            };
        }
    } catch {
        trainingStore.plan = { name: "Мій план", days: {} };
    }

    ensurePlanStructure();
    syncWorkoutWithPlanToday();
}

export function syncWorkoutWithPlanToday() {
    const dayKey = getTodayKey();
    const day = trainingStore.plan.days[dayKey] || { exercises: [] };

    trainingStore.workout = [];

    day.exercises.forEach(item => {
        const exObj = trainingStore.exercises.find(e => e.id === item.exercise.id);
        if (!exObj) return;

        trainingStore.workout.push({
            exercise: exObj,
            sets: item.sets ?? 3,
            reps: item.reps ?? "8-12",
            load: item.load ?? 0,
            done: false
        });
    });

    renderWorkoutList();
}

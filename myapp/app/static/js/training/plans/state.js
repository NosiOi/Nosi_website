import { DAYS } from "./constants.js";

export const state = {
    currentDay: "mon",
    days: {}
};

export function initState(loadExisting = false) {
    if (loadExisting && window.trainingStore.plan?.days) {
        state.days = normalize(window.trainingStore.plan.days);
    } else {
        state.days = normalize({});
    }
}

export function normalize(raw) {
    const out = {};
    DAYS.forEach(day => {
        const val = raw[day];
        if (Array.isArray(val)) out[day] = val;
        else if (val && Array.isArray(val.exercises)) out[day] = val.exercises;
        else out[day] = [];
    });
    return out;
}

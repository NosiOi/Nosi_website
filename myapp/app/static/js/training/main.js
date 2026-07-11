import { TrainingAPI } from "./api.js";
import { trainingStore } from "./store.js";
import { renderCurrentDate, renderAnalytics, renderStrengthTestResults } from "./dashboard.js";
import { loadPlan } from "./plans.js";
import { renderWorkoutList } from "./workout.js";
import { openExercisePicker } from "./exercise_picker.js";
import { initSession } from "./session.js";
import { initPlanModal } from "./plan_modal.js";

document.addEventListener("DOMContentLoaded", async () => {
    renderCurrentDate();

    const exData = await TrainingAPI.getExercises();
    trainingStore.exercises = exData.items || exData || [];

    await loadPlan();

    const analytics = await TrainingAPI.getAnalytics();
    renderAnalytics(analytics);
    renderStrengthTestResults(analytics.raw_performance || analytics.performance_raw || analytics);

    TrainingAPI.getRecommendations().then(renderRecommendations);

    const addExercise = document.getElementById("tr-add-exercise");
    if (addExercise) {
        addExercise.onclick = () => {
            openExercisePicker(ex => {
                trainingStore.workout.push({
                    exercise: ex,
                    sets: 3,
                    reps: "8-12",
                    load: 0,
                    done: false
                });
                renderWorkoutList();
            });
        };
    }

    initSession();
    initPlanModal();
    renderWorkoutList();
});

import { trainingStore } from "./store.js";
import { renderWorkoutList } from "./workout.js";
import { loadPlan } from "./plans.js";

export function initSession() {
    const saveWorkout = document.getElementById("tr-save-workout");
    if (!saveWorkout) return;

    saveWorkout.onclick = () => {
        if (!trainingStore.workout.length) return;

        const titleInput = document.getElementById("tr-workout-title");
        const title = titleInput ? titleInput.value.trim() : "";

        const payloadExercises = trainingStore.workout.map(item => ({
            exercise: { id: item.exercise.id },
            sets: item.sets ?? 3,
            reps: item.reps ?? "8-12",
            load: item.load ?? 0
        }));

        const btn = saveWorkout;
        btn.disabled = true;

        TrainingAPI.completeSession({
            title,
            exercises: payloadExercises
        }).then(() => {
            trainingStore.workout = [];
            if (titleInput) titleInput.value = "";
            renderWorkoutList();
            TrainingAPI.getHeatmap().then(() => {});
            loadPlan();
        }).finally(() => {
            btn.disabled = false;
        });
    };
}

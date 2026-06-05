from typing import List
from ..exercises.exercise_loader import ExerciseLoader
from ..exercises.exercise_classifier import ExerciseClassifier


class PlanAdapter:

    # Adapts exercises to user's environment: home, outdoor, gym

    @staticmethod
    def pick_for_muscle(muscle: str, environment: str) -> List:
        all_ex = ExerciseLoader.all()
        candidates = ExerciseClassifier.by_primary_muscle(all_ex, muscle)

        return [
            ex for ex in candidates
            if environment in ex.environment
        ][:3]

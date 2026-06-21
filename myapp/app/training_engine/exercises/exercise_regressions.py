from typing import Optional, List
from ..models.exercise import Exercise
from .exercise_loader import ExerciseLoader


class ExerciseRegressions:
    @staticmethod
    def previous_regression(exercise: Exercise) -> Optional[Exercise]:
        chain = exercise.regression_chain
        if not chain:
            return None
        try:
            idx = chain.index(exercise.id)
            prev_id = chain[idx - 1]
            return ExerciseLoader.get(prev_id)
        except (ValueError, IndexError):
            return None

    @staticmethod
    def full_regression_chain(exercise: Exercise) -> List[Exercise]:
        return [
            ExerciseLoader.get(ex_id)
            for ex_id in exercise.regression_chain
            if ExerciseLoader.get(ex_id)
        ]

    @staticmethod
    def should_regress(exercise: Exercise, fatigue_score: float) -> bool:
        return fatigue_score > 5

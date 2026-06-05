from typing import List, Optional
from ..models.exercise import Exercise
from .exercise_loader import ExerciseLoader


class ExerciseProgressions:

    @staticmethod
    def next_progression(exercise: Exercise) -> Optional[Exercise]:
        chain = exercise.progression_chain
        if not chain:
            return None

        try:
            idx = chain.index(exercise.id)
            next_id = chain[idx + 1]
            return ExerciseLoader.get(next_id)
        except (ValueError, IndexError):
            return None

    @staticmethod
    def full_progression_chain(exercise: Exercise) -> List[Exercise]:
        return [
            ExerciseLoader.get(ex_id)
            for ex_id in exercise.progression_chain
            if ExerciseLoader.get(ex_id)
        ]

    @staticmethod
    def can_progress(exercise: Exercise, performance_score: float) -> bool:
        """
        Placeholder logic:
        - if performance_score > difficulty * 10 → progress
        """
        return performance_score > exercise.difficulty * 10

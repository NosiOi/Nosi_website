from typing import List, Dict
from ..exercises.exercise_loader import ExerciseLoader
from ..exercises.exercise_classifier import ExerciseClassifier


class ExerciseRecommendations:
    
    # Suggests exercises based on: weak points, strong points, environment

    @staticmethod
    def for_weak_points(weak_points: List[str], environment: str) -> Dict[str, List]:
        all_ex = ExerciseLoader.all()
        result = {}

        for muscle in weak_points:
            candidates = ExerciseClassifier.by_primary_muscle(all_ex, muscle)
            filtered = [ex for ex in candidates if environment in ex.environment]
            result[muscle] = filtered[:3]

        return result

    @staticmethod
    def for_goal(goal: str, environment: str) -> List:
        all_ex = ExerciseLoader.all()

        if goal == "gain":
            return [ex for ex in all_ex.values() if ex.difficulty >= 4 and environment in ex.environment][:5]

        if goal == "lose":
            return [ex for ex in all_ex.values() if ex.movement_pattern in ["squat", "hinge", "push"]][:5]

        if goal == "maintain":
            return [ex for ex in all_ex.values() if environment in ex.environment][:5]

        return []

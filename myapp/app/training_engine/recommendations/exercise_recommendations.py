from typing import List, Dict
from ..exercises.exercise_loader import ExerciseLoader
from ..exercises.exercise_classifier import ExerciseClassifier


class ExerciseRecommendations:
    @staticmethod
    def for_weak_points(weak_points: List[str], environment: str) -> Dict[str, List]:
        all_ex = ExerciseLoader.all()
        result = {}

        for muscle in weak_points or []:
            candidates = ExerciseClassifier.by_primary_muscle(all_ex, muscle)
            filtered = [ex for ex in candidates if environment in ex.environment]
            result[muscle] = filtered[:3]

        return result

    @staticmethod
    def for_goal(goal: str, environment: str) -> List:
        all_ex = ExerciseLoader.all()

        def env_ok(ex):
            envs = ex.environment if isinstance(ex.environment, (list, tuple)) else [ex.environment]
            return environment in envs

        if goal == "gain":
            candidates = [
                ex for ex in all_ex.values()
                if ex.difficulty_level >= 4 and env_ok(ex)
            ]
            return candidates[:5]

        if goal == "lose":
            return [
                ex for ex in all_ex.values()
                if (ex.movement_pattern or "") in ("squat", "hinge", "push")
            ][:5]

        if goal == "maintain":
            return [ex for ex in all_ex.values() if env_ok(ex)][:5]

        return []

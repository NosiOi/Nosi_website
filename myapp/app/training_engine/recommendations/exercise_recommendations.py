from typing import List, Dict
from ..exercises.exercise_loader import ExerciseLoader
from ..exercises.exercise_classifier import ExerciseClassifier


class ExerciseRecommendations:
    # Suggests exercises based on: weak points, strong points, environment

    @staticmethod
    def for_weak_points(weak_points: List[str], environment: str) -> Dict[str, List]:
        all_ex = ExerciseLoader.all() or {}
        result: Dict[str, List] = {}

        for muscle in weak_points or []:
            candidates = ExerciseClassifier.by_primary_muscle(all_ex, muscle) or []
            filtered = []
            for ex in candidates:
                try:
                    envs = ex.environment if isinstance(ex.environment, (list, tuple)) else (ex.environment or [])
                except Exception:
                    envs = []
                if environment in envs:
                    filtered.append(ex)
            result[muscle] = filtered[:3]

        return result

    @staticmethod
    def for_goal(goal: str, environment: str) -> List:
        all_ex = ExerciseLoader.all() or {}

        def env_matches(ex):
            try:
                envs = ex.environment if isinstance(ex.environment, (list, tuple)) else (ex.environment or [])
            except Exception:
                envs = []
            return environment in envs

        if goal == "gain":
            candidates = []
            for ex in all_ex.values():
                try:
                    diff = getattr(ex, "difficulty_level", None)
                    if diff is None:
                        diff = int(getattr(ex, "difficulty", 1) or 1)
                except Exception:
                    diff = 1
                if diff >= 4 and env_matches(ex):
                    candidates.append(ex)
            return candidates[:5]

        if goal == "lose":
            candidates = []
            for ex in all_ex.values():
                try:
                    mp = getattr(ex, "movement_pattern", None) or ""
                except Exception:
                    mp = ""
                if mp in ("squat", "hinge", "push"):
                    candidates.append(ex)
            return candidates[:5]

        if goal == "maintain":
            return [ex for ex in all_ex.values() if env_matches(ex)][:5]

        return []

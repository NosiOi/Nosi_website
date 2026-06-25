from typing import List, Dict
from myapp.app.training_engine.models.exercise import Exercise
from myapp.app.training_engine.models.muscle import Muscle


class ExerciseRecommendations:

    @staticmethod
    def for_weak_points(weak_points: List[str], environment: str) -> Dict[str, List]:
        result = {}

        for muscle_slug in weak_points or []:
            q = Exercise.query.join(Exercise.muscles).filter(Muscle.slug == muscle_slug)

            if environment:
                q = q.filter(Exercise.location.in_([environment, "any"]))

            result[muscle_slug] = [ex.to_dict() for ex in q.limit(5).all()]

        return result

    @staticmethod
    def for_goal(goal: str, environment: str) -> List[Dict]:
        q = Exercise.query

        if environment:
            q = q.filter(Exercise.location.in_([environment, "any"]))

        if goal == "gain":
            q = q.filter(Exercise.difficulty >= 4)
            return [ex.to_dict() for ex in q.limit(5).all()]

        if goal == "lose":
            patterns = ["squat", "hinge", "push"]
            q = q.filter(Exercise.movement_pattern.in_(patterns))
            return [ex.to_dict() for ex in q.limit(5).all()]

        if goal == "maintain":
            return [ex.to_dict() for ex in q.limit(5).all()]

        return []

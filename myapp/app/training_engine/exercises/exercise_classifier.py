from typing import List, Dict
from ..models.exercise import Exercise


class ExerciseClassifier:

    @staticmethod
    def by_primary_muscle(exercises: Dict[str, Exercise], muscle: str) -> List[Exercise]:
        return [ex for ex in exercises.values() if muscle in ex.muscles_primary]

    @staticmethod
    def by_movement_pattern(exercises: Dict[str, Exercise], pattern: str) -> List[Exercise]:
        return [ex for ex in exercises.values() if ex.movement_pattern == pattern]

    @staticmethod
    def by_difficulty(exercises: Dict[str, Exercise], min_d: int, max_d: int) -> List[Exercise]:
        return [ex for ex in exercises.values() if min_d <= ex.difficulty <= max_d]

    @staticmethod
    def by_equipment(exercises: Dict[str, Exercise], equipment: str) -> List[Exercise]:
        return [ex for ex in exercises.values() if equipment in ex.equipment]

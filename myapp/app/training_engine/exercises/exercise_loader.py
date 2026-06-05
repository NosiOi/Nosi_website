import json
import os
from typing import Dict
from ..models.exercise import Exercise


class ExerciseLoader:

    _cache: Dict[str, Exercise] = {}

    @classmethod
    def load_base_exercises(cls, base_path: str):
        file_path = os.path.join(base_path, "base_exercises.json")

        with open(file_path, "r", encoding="utf-8") as f:
            data = json.load(f)

        for ex_id, ex_data in data.items():
            cls._cache[ex_id] = Exercise(
                id=ex_data["id"],
                name=ex_data["name"],
                muscles_primary=ex_data["muscles_primary"],
                muscles_secondary=ex_data.get("muscles_secondary", []),
                difficulty=ex_data.get("difficulty", 1),
                equipment=ex_data.get("equipment", []),
                environment=ex_data.get("environment", []),
                movement_pattern=ex_data.get("movement_pattern"),
                risk_level=ex_data.get("risk_level", 1),
                progression_chain=ex_data.get("progression_chain", []),
                regression_chain=ex_data.get("regression_chain", []),
            )

    @classmethod
    def get(cls, exercise_id: str) -> Exercise:
        return cls._cache.get(exercise_id)

    @classmethod
    def all(cls) -> Dict[str, Exercise]:
        return cls._cache

    @classmethod
    def filter_by_environment(cls, env: str) -> Dict[str, Exercise]:
        return {
            k: v for k, v in cls._cache.items()
            if env in v.environment
        }

import json
import tempfile
import os
from myapp.app.training_engine.exercises.exercise_loader import ExerciseLoader


def test_exercise_loader_loads_exercises():
    # Create temporary directory
    with tempfile.TemporaryDirectory() as tmp:
        path = os.path.join(tmp, "base_exercises.json")

        # Minimal exercise dataset
        data = {
            "pushups": {
                "id": "pushups",
                "name": "Push Ups",
                "muscles_primary": ["chest"],
                "difficulty": 3,
                "equipment": ["bodyweight"],
                "environment": ["home"],
                "movement_pattern": "push",
                "risk_level": 1
            }
        }

        with open(path, "w", encoding="utf-8") as f:
            json.dump(data, f)

        ExerciseLoader._cache = {}  # reset cache
        ExerciseLoader.load_base_exercises(tmp)

        ex = ExerciseLoader.get("pushups")

        assert ex is not None
        assert ex.name == "Push Ups"
        assert ex.movement_pattern == "push"
        assert "chest" in ex.muscles_primary

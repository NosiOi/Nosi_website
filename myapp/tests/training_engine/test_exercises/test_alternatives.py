from myapp.app.training_engine.exercises.exercise_alternatives import ExerciseAlternatives
from myapp.app.training_engine.exercises.exercise_loader import ExerciseLoader
from myapp.app.training_engine.models.exercise import Exercise


def setup_module(module):
    ExerciseLoader._cache = {
        "pushups": Exercise(
            id="pushups",
            name="Push Ups",
            muscles_primary=["chest"],
            movement_pattern="push",
            difficulty=3,
            equipment=["bodyweight"],
            environment=["home"]
        ),
        "bench": Exercise(
            id="bench",
            name="Bench Press",
            muscles_primary=["chest"],
            movement_pattern="push",
            difficulty=5,
            equipment=["barbell"],
            environment=["gym"]
        )
    }


def test_alternatives_by_muscle():
    ex = ExerciseLoader.get("pushups")
    result = ExerciseAlternatives.by_muscle(ex)

    assert len(result) >= 1
    assert result[0].muscles_primary[0] == "chest"


def test_alternatives_similar_difficulty():
    ex = ExerciseLoader.get("pushups")
    result = ExerciseAlternatives.similar_difficulty(ex, delta=2)

    assert any(r.id == "bench" or r.id == "pushups" for r in result)

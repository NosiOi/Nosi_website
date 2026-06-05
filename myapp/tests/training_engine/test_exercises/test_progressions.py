from myapp.app.training_engine.exercises.exercise_progressions import ExerciseProgressions
from myapp.app.training_engine.models.exercise import Exercise
from myapp.app.training_engine.exercises.exercise_loader import ExerciseLoader


def test_next_progression():
    ExerciseLoader._cache = {
        "incline": Exercise(id="incline", name="Incline", muscles_primary=["chest"]),
        "pushups": Exercise(id="pushups", name="Push Ups", muscles_primary=["chest"]),
        "decline": Exercise(id="decline", name="Decline", muscles_primary=["chest"])
    }

    ex = Exercise(
        id="pushups",
        name="Push Ups",
        muscles_primary=["chest"],
        progression_chain=["incline", "pushups", "decline"]
    )

    next_ex = ExerciseProgressions.next_progression(ex)

    assert next_ex.id == "decline"


def test_can_progress():
    ex = Exercise(id="pushups", name="Push Ups", muscles_primary=["chest"], difficulty=3)

    assert ExerciseProgressions.can_progress(ex, performance_score=40) is True
    assert ExerciseProgressions.can_progress(ex, performance_score=10) is False

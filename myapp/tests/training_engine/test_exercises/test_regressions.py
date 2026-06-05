from myapp.app.training_engine.exercises.exercise_regressions import ExerciseRegressions
from myapp.app.training_engine.models.exercise import Exercise
from myapp.app.training_engine.exercises.exercise_loader import ExerciseLoader


def test_previous_regression():
    ExerciseLoader._cache = {
        "wall": Exercise(id="wall", name="Wall Push", muscles_primary=["chest"]),
        "incline": Exercise(id="incline", name="Incline", muscles_primary=["chest"]),
        "pushups": Exercise(id="pushups", name="Push Ups", muscles_primary=["chest"])
    }

    ex = Exercise(
        id="incline",
        name="Incline",
        muscles_primary=["chest"],
        regression_chain=["wall", "incline", "pushups"]
    )

    prev_ex = ExerciseRegressions.previous_regression(ex)

    assert prev_ex.id == "wall"


def test_should_regress():
    ex = Exercise(id="pushups", name="Push Ups", muscles_primary=["chest"])

    assert ExerciseRegressions.should_regress(ex, fatigue_score=7) is True
    assert ExerciseRegressions.should_regress(ex, fatigue_score=3) is False

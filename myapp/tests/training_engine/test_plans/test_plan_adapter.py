from myapp.app.training_engine.plans.plan_adapter import PlanAdapter
from myapp.app.training_engine.exercises.exercise_loader import ExerciseLoader
from myapp.app.training_engine.models.exercise import Exercise


def setup_module(module):
    ExerciseLoader._cache = {
        "pushups": Exercise(
            id="pushups",
            name="Push Ups",
            muscles_primary=["chest"],
            environment=["home"]
        ),
        "bench": Exercise(
            id="bench",
            name="Bench Press",
            muscles_primary=["chest"],
            environment=["gym"]
        )
    }


def test_pick_for_muscle_home():
    result = PlanAdapter.pick_for_muscle("chest", "home")
    assert len(result) == 1
    assert result[0].id == "pushups"


def test_pick_for_muscle_gym():
    result = PlanAdapter.pick_for_muscle("chest", "gym")
    assert len(result) == 1
    assert result[0].id == "bench"

from myapp.app.training_engine.recommendations.exercise_recommendations import ExerciseRecommendations
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
        ),
        "squats": Exercise(
            id="squats",
            name="Squats",
            muscles_primary=["legs"],
            environment=["home", "gym"]
        )
    }


def test_exercise_recommendations_for_weak_points():
    result = ExerciseRecommendations.for_weak_points(
        weak_points=["chest"],
        environment="home"
    )

    assert "chest" in result
    assert len(result["chest"]) == 1
    assert result["chest"][0].id == "pushups"


def test_exercise_recommendations_for_goal_gain():
    result = ExerciseRecommendations.for_goal("gain", "gym")

    assert isinstance(result, list)
    assert len(result) > 0

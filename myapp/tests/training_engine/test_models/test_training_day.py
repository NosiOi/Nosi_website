from myapp.app.training_engine.models.training_day import TrainingDay
from myapp.app.training_engine.models.exercise import Exercise


def test_training_day_add_exercise():
    day = TrainingDay(day_name="day1", environment="gym")

    ex = Exercise(
        id="pushups",
        name="Віджимання",
        muscles_primary=["chest"]
    )

    day.add_exercise(exercise=ex, sets=3, reps="10-12")

    assert len(day.exercises) == 1
    assert day.exercises[0]["sets"] == 3
    assert day.exercises[0]["reps"] == "10-12"
    assert day.total_volume() == 3

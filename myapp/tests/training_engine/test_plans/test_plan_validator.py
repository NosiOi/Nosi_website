from myapp.app.training_engine.plans.plan_validator import PlanValidator
from myapp.app.training_engine.models.training_day import TrainingDay
from myapp.app.training_engine.models.exercise import Exercise


def test_plan_validator_valid():
    day = TrainingDay(day_name="day1")
    ex = Exercise(id="pushups", name="Push Ups", muscles_primary=["chest"])
    day.add_exercise(ex, sets=3, reps="10-12")

    days = {"day1": day}

    assert PlanValidator.validate_plan(days) is True


def test_plan_validator_empty_day():
    day = TrainingDay(day_name="day1")
    days = {"day1": day}

    try:
        PlanValidator.validate_plan(days)
        assert False  # should not reach here
    except ValueError:
        assert True

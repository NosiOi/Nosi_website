from myapp.app.training_engine.models.training_plan import TrainingPlan, TrainingDay


def test_training_plan_add_and_get_day():
    plan = TrainingPlan(goal="gain", experience="beginner", workouts_per_week=3)

    day = TrainingDay(day_name="day1")
    plan.add_day("day1", day)

    assert "day1" in plan.days
    assert plan.get_day("day1") is day
    assert plan.summary()["goal"] == "gain"

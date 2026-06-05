from myapp.app.training_engine.plans.plan_generator import PlanGenerator
from myapp.app.training_engine.models.user_profile_snapshot import UserProfileSnapshot
from myapp.app.training_engine.exercises.exercise_loader import ExerciseLoader
from myapp.app.training_engine.models.exercise import Exercise


def setup_module(module):
    # Minimal exercise dataset for plan generation
    ExerciseLoader._cache = {
        "pushups": Exercise(
            id="pushups",
            name="Push Ups",
            muscles_primary=["chest"],
            environment=["home", "gym"]
        ),
        "squats": Exercise(
            id="squats",
            name="Squats",
            muscles_primary=["legs"],
            environment=["home", "gym"]
        )
    }


def test_plan_generator_basic():
    profile = UserProfileSnapshot(
        age=20,
        sex="male",
        weight=70,
        height=180,
        activity=1.6,
        goal="gain",
        experience="beginner",
        workouts_per_week=3,
        environment="home",
        weak_points=["core"],
        strong_points=["chest"]
    )

    generator = PlanGenerator(profile)
    plan = generator.generate(week=1)

    assert len(plan.days) == 3
    for day in plan.days.values():
        assert len(day.exercises) > 0

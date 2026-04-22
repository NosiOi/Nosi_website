from myapp.app.services.plan_generator import PlanGenerator


def test_full_plan():
    gen = PlanGenerator(
        age=25,
        gender="male",
        weight=70,
        height=175,
        activity=1.55,
        goal="maintain",
        experience="beginner",
        workouts_per_week=3,
    )

    plan = gen.generate()

    assert "sleep" in plan
    assert "calories" in plan
    assert "macros" in plan
    assert "water_liters" in plan
    assert "training" in plan

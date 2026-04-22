from myapp.app.services.training_plan_generator import generate_training_plan


def test_training_beginner():
    plan = generate_training_plan("lose", "beginner", 2)
    assert plan["type"] == "full_body"
    assert plan["frequency"] == 2

from myapp.app.training_engine.models.exercise import Exercise


def test_exercise_basic_creation():
    ex = Exercise(
        id="pushups",
        name="Віджимання",
        muscles_primary=["chest"],
        muscles_secondary=["triceps"],
        difficulty=3,
        equipment=["bodyweight"],
        environment=["home", "gym"],
        movement_pattern="push",
        risk_level=1,
        progression_chain=["incline_pushups", "pushups", "decline_pushups"],
        regression_chain=["wall_pushups", "incline_pushups"]
    )

    assert ex.id == "pushups"
    assert ex.name == "Віджимання"
    assert "chest" in ex.muscles_primary
    assert ex.difficulty == 3
    assert ex.is_bodyweight() is True
    assert ex.is_safe_for_beginners() is True

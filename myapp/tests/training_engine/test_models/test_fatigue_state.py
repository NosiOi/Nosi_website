from myapp.app.training_engine.models.fatigue_state import FatigueState


def test_fatigue_state_score():
    fatigue = FatigueState(
        sleep_hours=6,
        stress_level=3,
        soreness_level=2
    )

    score = fatigue.fatigue_score()
    assert score > 0
    assert isinstance(score, float)

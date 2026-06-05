from myapp.app.training_engine.analytics.fatigue_model import FatigueModel


def test_fatigue_model_score():
    fm = FatigueModel(
        sleep_hours=6,
        stress=3,
        soreness=2,
        training_load=50
    )

    score = fm.fatigue_score()

    assert isinstance(score, float)
    assert score > 0


def test_fatigue_model_overtrained():
    fm = FatigueModel(
        sleep_hours=4,
        stress=5,
        soreness=5,
        training_load=200
    )

    assert fm.is_overtrained() is True

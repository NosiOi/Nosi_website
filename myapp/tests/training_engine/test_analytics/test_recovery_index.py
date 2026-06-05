from myapp.app.training_engine.analytics.recovery_index import RecoveryIndex


def test_recovery_index_score():
    ri = RecoveryIndex(
        sleep_hours=7,
        stress=2,
        soreness=2,
        hydration_liters=2.0
    )

    score = ri.score()

    assert isinstance(score, float)
    assert 0 <= score <= 100

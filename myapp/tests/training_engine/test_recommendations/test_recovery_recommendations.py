from myapp.app.training_engine.recommendations.recovery_recommendations import RecoveryRecommendations


def test_recovery_recommendations_low_sleep():
    result = RecoveryRecommendations.generate(
        sleep=5,
        stress=2,
        soreness=2,
        hydration=2.0
    )

    assert any("sleep" in rec.lower() for rec in result["recovery_recommendations"])


def test_recovery_recommendations_optimal():
    result = RecoveryRecommendations.generate(
        sleep=8,
        stress=1,
        soreness=1,
        hydration=2.5
    )

    assert "Recovery is optimal" in result["recovery_recommendations"][0]

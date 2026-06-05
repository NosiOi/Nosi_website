from myapp.app.training_engine.analytics.strength_index import StrengthIndex


def test_strength_index_basic():
    si = StrengthIndex(
        pushups=40,
        squats=50,
        situps=60,
        weight=70
    )

    score = si.score()
    breakdown = si.breakdown()

    assert isinstance(score, float)
    assert 0 <= score <= 100
    assert "push_strength" in breakdown
    assert breakdown["total_score"] == score

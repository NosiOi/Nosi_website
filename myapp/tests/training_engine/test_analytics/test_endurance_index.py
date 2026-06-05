from myapp.app.training_engine.analytics.endurance_index import EnduranceIndex


def test_endurance_index_score():
    ei = EnduranceIndex(
        pushups=30,
        squats=40,
        plank_sec=90,
        weight=70
    )

    score = ei.score()

    assert isinstance(score, float)
    assert 0 <= score <= 100

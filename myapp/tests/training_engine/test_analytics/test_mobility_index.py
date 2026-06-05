from myapp.app.training_engine.analytics.mobility_index import MobilityIndex


def test_mobility_index_score():
    mi = MobilityIndex(
        hip=4,
        shoulder=3,
        thoracic=5,
        ankle=4
    )

    score = mi.score()

    assert isinstance(score, float)
    assert 0 <= score <= 100
    assert score == round((4 + 3 + 5 + 4) / 20 * 100, 2)

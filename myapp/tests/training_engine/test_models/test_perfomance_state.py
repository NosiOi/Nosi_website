from myapp.app.training_engine.models.performance_state import PerformanceState


def test_performance_state_strength_index():
    perf = PerformanceState(
        pushups_max=30,
        squats_max=40,
        situps_max=50,
        plank_time_sec=60
    )

    score = perf.strength_index()
    assert score > 0
    assert isinstance(score, float)

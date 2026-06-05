from myapp.app.training_engine.progression.autoregulation import Autoregulation


def test_autoregulation_reduce_load_on_fatigue():
    auto = Autoregulation(fatigue_threshold=6.0, reduction_percent=0.2)
    new_load = auto.adjust_load(load=100, fatigue_score=7)
    assert new_load == 80


def test_autoregulation_keep_load_when_not_fatigued():
    auto = Autoregulation(fatigue_threshold=6.0)
    new_load = auto.adjust_load(load=100, fatigue_score=4)
    assert new_load == 100


def test_autoregulation_reduce_reps_on_fatigue():
    auto = Autoregulation(fatigue_threshold=6.0)
    new_reps = auto.adjust_reps(reps=10, fatigue_score=7)
    assert new_reps == 8


def test_autoregulation_keep_reps_when_not_fatigued():
    auto = Autoregulation(fatigue_threshold=6.0)
    new_reps = auto.adjust_reps(reps=10, fatigue_score=3)
    assert new_reps == 10

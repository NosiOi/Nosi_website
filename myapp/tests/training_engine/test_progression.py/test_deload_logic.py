from myapp.app.training_engine.progression.deload_logic import DeloadLogic


def test_deload_trigger_by_fatigue():
    dl = DeloadLogic(fatigue_trigger=8.0)
    assert dl.needs_deload(fatigue_score=9, high_rpe_sessions=0) is True


def test_deload_trigger_by_rpe_sessions():
    dl = DeloadLogic(rpe_trigger=3)
    assert dl.needs_deload(fatigue_score=3, high_rpe_sessions=3) is True


def test_deload_not_triggered():
    dl = DeloadLogic()
    assert dl.needs_deload(fatigue_score=5, high_rpe_sessions=1) is False


def test_deload_apply():
    dl = DeloadLogic(reduction_percent=0.3)

    updated = dl.apply_deload(load=100, reps=10, sets=4)

    assert updated["load"] == 70
    assert updated["reps"] == 7
    assert updated["sets"] == 2  # 4 * 0.7 = 2.8 → int() = 2

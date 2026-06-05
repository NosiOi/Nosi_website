from myapp.app.training_engine.progression.rpe_logic import RPELogic


def test_rpe_increase_load_on_low_rpe():
    rpe = RPELogic()
    new_load = rpe.adjust_load(load=100, rpe=6)
    assert new_load == 105  # +5%


def test_rpe_maintain_load_on_rpe_8():
    rpe = RPELogic()
    new_load = rpe.adjust_load(load=100, rpe=8)
    assert new_load == 100


def test_rpe_reduce_load_on_rpe_10():
    rpe = RPELogic()
    new_load = rpe.adjust_load(load=100, rpe=10)
    assert new_load == 90  # -10%


def test_rpe_adjust_reps():
    rpe = RPELogic()

    assert rpe.adjust_reps(10, 6) == 12
    assert rpe.adjust_reps(10, 7) == 11
    assert rpe.adjust_reps(10, 8) == 10
    assert rpe.adjust_reps(10, 9) == 9
    assert rpe.adjust_reps(10, 10) == 8

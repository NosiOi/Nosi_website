from myapp.app.training_engine.plans.plan_periodization import PlanPeriodization


def test_linear_periodization():
    p = PlanPeriodization.apply("linear", week=1)
    assert "intensity" in p
    assert p["intensity"] > 0.5


def test_wave_periodization():
    p1 = PlanPeriodization.apply("wave", week=1)
    p2 = PlanPeriodization.apply("wave", week=2)
    assert p1["intensity"] != p2["intensity"]


def test_block_periodization():
    deload_week = PlanPeriodization.apply("block", week=4)
    assert deload_week["intensity"] < 0.6
    assert deload_week["volume"] < 1.0

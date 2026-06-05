from myapp.app.training_engine.plans.plan_split_logic import PlanSplitLogic


def test_choose_split():
    assert PlanSplitLogic.choose_split(1) == "full_body_1"
    assert PlanSplitLogic.choose_split(3) == "full_body_3"
    assert PlanSplitLogic.choose_split(4) == "upper_lower"
    assert PlanSplitLogic.choose_split(6) == "ppl_x2"


def test_base_distribution_structure():
    split = PlanSplitLogic.choose_split(3)
    dist = PlanSplitLogic.base_distribution(split)

    assert isinstance(dist, dict)
    assert "day1" in dist
    assert isinstance(dist["day1"], list)
    assert len(dist["day1"]) > 0

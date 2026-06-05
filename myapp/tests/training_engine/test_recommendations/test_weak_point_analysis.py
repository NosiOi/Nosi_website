from myapp.app.training_engine.recommendations.weak_point_analysis import WeakPointAnalysis


def test_weak_point_analysis_detects_critical():
    result = WeakPointAnalysis.analyze(
        weak_points=["core", "chest"],
        strong_points=[]
    )

    assert "Critical weak zones detected" in result["weak_point_recommendations"][0]


def test_weak_point_analysis_no_weak_points():
    result = WeakPointAnalysis.analyze(
        weak_points=[],
        strong_points=["legs"]
    )

    assert "No major weak points detected" in result["weak_point_recommendations"][0]

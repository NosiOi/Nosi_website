from myapp.app.services.macros_calculator import calculate_macros


def test_macros_maintain():
    result = calculate_macros(70, 2500, "maintain")
    assert result["protein"] == 112
    assert result["fat"] == 70
    assert result["carbs"] > 200

from myapp.app.services.calories_calculator import (
    calculate_bmr,
    calculate_tdee,
    calculate_calories_goal,
)


def test_bmr_male():
    assert round(calculate_bmr(70, 175, 25, "male")) == 1668


def test_bmr_female():
    assert round(calculate_bmr(60, 165, 25, "female")) == 1405


def test_tdee():
    assert calculate_tdee(1600, 1.55) == 2480


def test_calories_goal_lose():
    assert calculate_calories_goal(2500, "lose") == 2125

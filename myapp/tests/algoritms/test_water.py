from myapp.app.services.water_calculator import calculate_water


def test_water():
    assert calculate_water(70) == 2.45

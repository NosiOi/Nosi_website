from myapp.app.services.sleep_calculator import calculate_sleep


def test_sleep_teenager():
    assert calculate_sleep(16) == (9, 10)


def test_sleep_young_adult():
    assert calculate_sleep(20) == (8, 9)


def test_sleep_adult():
    assert calculate_sleep(40) == (7, 8)


def test_sleep_senior():
    assert calculate_sleep(70) == (6, 7)

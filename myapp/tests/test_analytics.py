import pytest
from myapp.app.services.analytics_service import (
    compute_muscle_load_from_session,
    compute_muscle_load_from_sessions,
    normalize_scores,
    compute_weekly_report,
)


class MockMuscle:
    def __init__(self, slug):
        self.slug = slug


class MockExerciseMuscle:
    def __init__(self, muscle_slug, load_percent=None, is_primary=False):
        self.muscle = MockMuscle(muscle_slug)
        self.load_percent = load_percent
        self.is_primary = is_primary


class MockExercise:
    def __init__(self, id, em_list=None, muscles=None):
        self.id = id
        # em_list: list of MockExerciseMuscle
        self.exercise_muscles = em_list or []
        # muscles: list of MockMuscle
        self.muscles = muscles or []


def exercise_lookup_factory(ex_map):
    def lookup(ex_id):
        return ex_map.get(ex_id)
    return lookup


def test_single_session_with_load_percent():
    # exercise 1: chest primary 60, triceps secondary 20
    ex1 = MockExercise(1, em_list=[
        MockExerciseMuscle("chest", load_percent=60, is_primary=True),
        MockExerciseMuscle("triceps", load_percent=20, is_primary=False),
    ])
    ex_map = {1: ex1}
    session = {"exercises": [{"id": 1, "sets": 3, "reps": 10}]}
    lookup = exercise_lookup_factory(ex_map)
    raw = compute_muscle_load_from_session(session, lookup)
    # work = 3*10 = 30
    # chest: 60% * 30 /100 = 18
    # triceps: 20% * 30 /100 = 6
    assert raw["chest"] == pytest.approx(18.0)
    assert raw["triceps"] == pytest.approx(6.0)


def test_single_session_without_load_percent_distribute_evenly():
    # exercise 2: no exercise_muscles, muscles list has 2 muscles
    ex2 = MockExercise(2, muscles=[MockMuscle("back"), MockMuscle("biceps")])
    ex_map = {2: ex2}
    session = {"exercises": [{"id": 2, "sets": 2, "reps": 5}]}
    lookup = exercise_lookup_factory(ex_map)
    raw = compute_muscle_load_from_session(session, lookup)
    # work = 2*5 = 10, distributed equally -> 5 each
    assert raw["back"] == pytest.approx(5.0)
    assert raw["biceps"] == pytest.approx(5.0)


def test_aggregate_multiple_sessions_and_normalize():
    ex1 = MockExercise(1, em_list=[MockExerciseMuscle("chest", load_percent=50)])
    ex2 = MockExercise(2, muscles=[MockMuscle("legs")])
    ex_map = {1: ex1, 2: ex2}
    s1 = {"exercises": [{"id": 1, "sets": 4, "reps": 8}]}  # work 32 -> chest 50% -> 16
    s2 = {"exercises": [{"id": 2, "sets": 3, "reps": 10}]}  # work 30 -> legs 30
    lookup = exercise_lookup_factory(ex_map)
    raw = compute_muscle_load_from_sessions([s1, s2], lookup)
    assert raw["chest"] == pytest.approx(16.0)
    assert raw["legs"] == pytest.approx(30.0)
    norm = normalize_scores(raw)
    assert norm["chest"] == pytest.approx(round(16.0 / (16.0 + 30.0), 4))
    assert norm["legs"] == pytest.approx(round(30.0 / (16.0 + 30.0), 4))


def test_compute_weekly_report_structure():
    ex1 = MockExercise(1, em_list=[MockExerciseMuscle("core", load_percent=100)])
    ex_map = {1: ex1}
    s1 = {"exercises": [{"id": 1, "sets": 1, "reps": 10}]}
    lookup = exercise_lookup_factory(ex_map)
    report = compute_weekly_report([s1], lookup)
    assert "raw" in report and "normalized" in report
    assert report["raw"]["core"] == pytest.approx(10.0)
    assert report["normalized"]["core"] == pytest.approx(1.0)

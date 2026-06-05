from myapp.app.training_engine.progression.linear_progression import LinearProgression


def test_linear_progression_increase_load():
    lp = LinearProgression(increment_percent=0.1)  # +10%
    result = lp.next_load(current_load=100, completed=True)
    assert result == 110


def test_linear_progression_no_increase_when_not_completed():
    lp = LinearProgression(increment_percent=0.1)
    result = lp.next_load(current_load=100, completed=False)
    assert result == 100


def test_linear_progression_increase_reps():
    lp = LinearProgression(rep_increment=3)
    result = lp.next_reps(current_reps=10, completed=True)
    assert result == 13


def test_linear_progression_apply():
    lp = LinearProgression(increment_percent=0.1, rep_increment=2)

    data = {"load": 50, "reps": 8, "sets": 3}
    updated = lp.apply(data, completed=True)

    assert updated["load"] == 55
    assert updated["reps"] == 10
    assert updated["sets"] == 3

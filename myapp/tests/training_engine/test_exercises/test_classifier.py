from myapp.app.training_engine.exercises.exercise_classifier import ExerciseClassifier
from myapp.app.training_engine.models.exercise import Exercise


def test_classifier_by_primary_muscle():
    ex1 = Exercise(id="pushups", name="Push Ups", muscles_primary=["chest"])
    ex2 = Exercise(id="squats", name="Squats", muscles_primary=["legs"])

    exercises = {"pushups": ex1, "squats": ex2}

    chest_ex = ExerciseClassifier.by_primary_muscle(exercises, "chest")

    assert len(chest_ex) == 1
    assert chest_ex[0].id == "pushups"


def test_classifier_by_movement_pattern():
    ex = Exercise(id="pushups", name="Push Ups", muscles_primary=["chest"], movement_pattern="push")
    exercises = {"pushups": ex}

    result = ExerciseClassifier.by_movement_pattern(exercises, "push")

    assert len(result) == 1
    assert result[0].movement_pattern == "push"

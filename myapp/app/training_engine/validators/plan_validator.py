from typing import Dict
from ..models.training_day import TrainingDay


class PlanValidator:
    
    # Ensures: each day has exercises, exercises have sets/reps, no empty days

    @staticmethod
    def validate_day(day: TrainingDay):
        if not day.exercises:
            raise ValueError(f"Training day '{day.day_name}' has no exercises")

        for ex in day.exercises:
            if "exercise" not in ex:
                raise ValueError("Exercise entry missing 'exercise' field")
            if "sets" not in ex or ex["sets"] <= 0:
                raise ValueError("Exercise must have valid sets")
            if "reps" not in ex:
                raise ValueError("Exercise must have reps")

    @staticmethod
    def validate_plan(days: Dict[str, TrainingDay]):
        if not days:
            raise ValueError("Training plan has no days")

        for name, day in days.items():
            PlanValidator.validate_day(day)

        return True

from typing import Dict
from ..models.training_plan import TrainingPlan as ORMTrainingPlan
from ..models.training_day import TrainingDay
from .plan_split_logic import PlanSplitLogic
from .plan_adapter import PlanAdapter
from .plan_periodization import PlanPeriodization
from .plan_validator import PlanValidator


class PlanGenerator:

    def __init__(self, profile_snapshot):
        self.profile = profile_snapshot

    def generate(self, week: int = 1) -> ORMTrainingPlan:
        split = PlanSplitLogic.choose_split(self.profile.workouts_per_week)
        distribution = PlanSplitLogic.base_distribution(split)

        period = PlanPeriodization.apply("linear", week)

        all_kwargs = {
            "goal": getattr(self.profile, "goal", None),
            "experience": getattr(self.profile, "experience", None),
            "workouts_per_week": getattr(self.profile, "workouts_per_week", None),
            "periodization": "linear"
        }

        try:
            allowed = {c.name for c in ORMTrainingPlan.__table__.columns}
        except Exception:
            allowed = set(all_kwargs.keys())

        filtered = {k: v for k, v in all_kwargs.items() if k in allowed}

        plan = ORMTrainingPlan(**filtered)

        for day_name, muscles in distribution.items():
            day = TrainingDay(day_name=day_name, environment=getattr(self.profile, "environment", None))

            for muscle in muscles:
                exercises = PlanAdapter.pick_for_muscle(muscle, getattr(self.profile, "environment", None))

                for ex in exercises:
                    day.add_exercise(
                        exercise=ex,
                        sets=3,
                        reps="8-12"
                    )

            plan.add_day(day_name, day)

        if not PlanValidator.validate(plan.days):
            raise ValueError("Generated plan is invalid")

        return plan

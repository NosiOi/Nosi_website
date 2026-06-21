from typing import Dict
from ..models.training_plan import TrainingPlan as ORMTrainingPlan
from ..models.training_day import TrainingDay as ORMTrainingDay
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

        PlanPeriodization.apply("linear", week)

        plan = ORMTrainingPlan(
            user_id=getattr(self.profile, "user_id", None),
            name="Training Plan",
            is_active=False
        )

        for day_name, muscles in distribution.items():
            day = ORMTrainingDay(day_name=day_name, environment=self.profile.environment)

            for muscle in muscles:
                exercises = PlanAdapter.pick_for_muscle(muscle, self.profile.environment) or []
                for ex in exercises:
                    day.add_exercise(exercise=ex, sets=3, reps="8-12")

            plan.add_day(day_name, day)

        if not PlanValidator.validate(plan.days):
            raise ValueError("Generated plan is invalid")

        return plan

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

    def _filter_kwargs_for_model(self, model_cls, kwargs: Dict):
        try:
            allowed = {c.name for c in model_cls.__table__.columns}
        except Exception:
            allowed = set(kwargs.keys())
        return {k: v for k, v in kwargs.items() if k in allowed}

    def generate(self, week: int = 1) -> ORMTrainingPlan:
        split = PlanSplitLogic.choose_split(getattr(self.profile, "workouts_per_week", 3))
        distribution = PlanSplitLogic.base_distribution(split)

        period = PlanPeriodization.apply("linear", week)

        plan_kwargs = {
            "goal": getattr(self.profile, "goal", None),
            "experience": getattr(self.profile, "experience", None),
            "workouts_per_week": getattr(self.profile, "workouts_per_week", None),
            "periodization": "linear"
        }

        filtered_plan_kwargs = self._filter_kwargs_for_model(ORMTrainingPlan, plan_kwargs)
        plan = ORMTrainingPlan(**filtered_plan_kwargs)

        for day_name, muscles in distribution.items():
            day_kwargs = {
                "name": day_name,
                "environment": getattr(self.profile, "environment", None),
            }
            filtered_day_kwargs = self._filter_kwargs_for_model(ORMTrainingDay, day_kwargs)

            try:
                day = ORMTrainingDay(**filtered_day_kwargs)
            except TypeError:
                day = ORMTrainingDay()
                for k, v in filtered_day_kwargs.items():
                    try:
                        setattr(day, k, v)
                    except Exception:
                        pass

            for muscle in muscles:
                exercises = PlanAdapter.pick_for_muscle(muscle, getattr(self.profile, "environment", None)) or []

                for ex in exercises:
                    try:
                        day.add_exercise(
                            exercise=ex,
                            sets=3,
                            reps="8-12"
                        )
                    except Exception:
                        try:
                            if not hasattr(day, "exercises") or day.exercises is None:
                                day.exercises = []
                            day.exercises.append({"exercise": ex, "sets": 3, "reps": "8-12"})
                        except Exception:
                            pass

            try:
                plan.add_day(day_name, day)
            except Exception:
                try:
                    if not hasattr(plan, "days") or plan.days is None:
                        plan.days = {}
                    plan.days[day_name] = day
                except Exception:
                    pass

        if not PlanValidator.validate(getattr(plan, "days", {})):
            raise ValueError("Generated plan is invalid")

        return plan

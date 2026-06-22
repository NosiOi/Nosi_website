from myapp.app.training_engine import (
    PlanGenerator,
    StrengthIndex,
    EnduranceIndex,
    MobilityIndex,
    RecoveryIndex,
    FatigueModel,
    UserProfileSnapshot
)
from myapp.app.training_engine.models.training_day import TrainingDay
from myapp.app.training_engine.models.exercise import Exercise


class TrainingEngineService:

    @staticmethod
    def _safe(obj, attr, default=None):
        try:
            val = getattr(obj, attr, default)
        except Exception:
            return default
        return default if val is None else val

    @staticmethod
    def build_profile(user):
        age = TrainingEngineService._safe(user, "age", 25)
        sex = TrainingEngineService._safe(user, "sex", "unspecified")
        weight = TrainingEngineService._safe(user, "weight", 70)
        height = TrainingEngineService._safe(user, "height", 175)
        activity = TrainingEngineService._safe(user, "activity", "moderate")
        goal = TrainingEngineService._safe(user, "goal", "maintenance")
        experience = TrainingEngineService._safe(user, "experience", "beginner")
        workouts_per_week = TrainingEngineService._safe(user, "workouts_per_week", 3)
        environment = TrainingEngineService._safe(user, "environment", "gym")
        weak_points = TrainingEngineService._safe(user, "weak_points", []) or []
        strong_points = TrainingEngineService._safe(user, "strong_points", []) or []

        return UserProfileSnapshot(
            age=age,
            sex=sex,
            weight=weight,
            height=height,
            activity=activity,
            goal=goal,
            experience=experience,
            workouts_per_week=workouts_per_week,
            environment=environment,
            weak_points=weak_points,
            strong_points=strong_points,
        )

    @staticmethod
    def generate_plan(user, week=1):
        profile = TrainingEngineService.build_profile(user)
        generator = PlanGenerator(profile)

        try:
            plan = generator.generate(week)
        except Exception:
            plan = None

        if not plan or not getattr(plan, "days", None):
            day = TrainingDay(day_name="day1", name="Day 1", environment=[profile.environment], exercises=[])
            exs = Exercise.query.order_by(Exercise.difficulty.asc()).limit(6).all()
            for ex in exs:
                day.add_exercise(exercise=ex, sets=3, reps="8-12")

            class SimplePlan:
                def __init__(self, days):
                    self.days = days

                def to_dict(self):
                    return {"days": self.days}

            plan = SimplePlan({"day1": day})

        normalized = {}
        for key, day in plan.days.items():
            if hasattr(day, "to_dict"):
                normalized[key] = day.to_dict()
            else:
                normalized[key] = dict(day)

        plan.days = normalized
        return plan

    @staticmethod
    def compute_analytics(performance, recovery):
        strength = StrengthIndex(
            pushups=TrainingEngineService._safe(performance, "pushups", 0),
            squats=TrainingEngineService._safe(performance, "squats", 0),
            situps=TrainingEngineService._safe(performance, "situps", 0),
            weight=TrainingEngineService._safe(performance, "weight", 70)
        ).score()

        endurance = EnduranceIndex(
            pushups=TrainingEngineService._safe(performance, "pushups", 0),
            squats=TrainingEngineService._safe(performance, "squats", 0),
            plank_sec=TrainingEngineService._safe(performance, "plank_sec", 0),
            weight=TrainingEngineService._safe(performance, "weight", 70)
        ).score()

        mobility = MobilityIndex(
            hip=TrainingEngineService._safe(performance, "hip", 0),
            shoulder=TrainingEngineService._safe(performance, "shoulder", 0),
            thoracic=TrainingEngineService._safe(performance, "thoracic", 0),
            ankle=TrainingEngineService._safe(performance, "ankle", 0)
        ).score()

        recovery_score = RecoveryIndex(
            sleep_hours=TrainingEngineService._safe(recovery, "sleep", 7),
            stress=TrainingEngineService._safe(recovery, "stress", 0),
            soreness=TrainingEngineService._safe(recovery, "soreness", 0),
            hydration_liters=TrainingEngineService._safe(recovery, "hydration", 2.0)
        ).score()

        fatigue = FatigueModel(
            sleep_hours=TrainingEngineService._safe(recovery, "sleep", 7),
            stress=TrainingEngineService._safe(recovery, "stress", 0),
            soreness=TrainingEngineService._safe(recovery, "soreness", 0),
            training_load=TrainingEngineService._safe(performance, "training_load", 0)
        ).fatigue_score()

        return {
            "strength": strength,
            "endurance": endurance,
            "mobility": mobility,
            "recovery": recovery_score,
            "fatigue": fatigue
        }

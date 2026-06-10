from myapp.app.training_engine import (
    PlanGenerator,
    StrengthIndex,
    EnduranceIndex,
    MobilityIndex,
    RecoveryIndex,
    FatigueModel,
    UserProfileSnapshot
)


class TrainingEngineService:

    @staticmethod
    def _safe(user, attr, default=None):
        try:
            return getattr(user, attr, default)
        except Exception:
            return default

    @staticmethod
    def build_profile(user):
        return UserProfileSnapshot(
            age=TrainingEngineService._safe(user, "age", 30),
            sex=TrainingEngineService._safe(user, "sex", "unspecified"),
            weight=TrainingEngineService._safe(user, "weight", None),
            height=TrainingEngineService._safe(user, "height", None),
            activity=TrainingEngineService._safe(user, "activity", None),
            goal=TrainingEngineService._safe(user, "goal", "maintenance"),
            experience=TrainingEngineService._safe(user, "experience", "beginner"),
            workouts_per_week=TrainingEngineService._safe(user, "workouts_per_week", 3),
            environment=TrainingEngineService._safe(user, "environment", "gym"),
            weak_points=TrainingEngineService._safe(user, "weak_points", []) or [],
            strong_points=TrainingEngineService._safe(user, "strong_points", []) or []
        )

    @staticmethod
    def generate_plan(user, week=1):
        profile = TrainingEngineService.build_profile(user)
        generator = PlanGenerator(profile)
        return generator.generate(week)

    @staticmethod
    def compute_analytics(performance, recovery):
        strength = StrengthIndex(
            pushups=TrainingEngineService._safe(performance, "pushups", 0),
            squats=TrainingEngineService._safe(performance, "squats", 0),
            situps=TrainingEngineService._safe(performance, "situps", 0),
            weight=TrainingEngineService._safe(performance, "weight", None)
        ).score()

        endurance = EnduranceIndex(
            pushups=TrainingEngineService._safe(performance, "pushups", 0),
            squats=TrainingEngineService._safe(performance, "squats", 0),
            plank_sec=TrainingEngineService._safe(performance, "plank_sec", 0),
            weight=TrainingEngineService._safe(performance, "weight", None)
        ).score()

        mobility = MobilityIndex(
            hip=TrainingEngineService._safe(performance, "hip", None),
            shoulder=TrainingEngineService._safe(performance, "shoulder", None),
            thoracic=TrainingEngineService._safe(performance, "thoracic", None),
            ankle=TrainingEngineService._safe(performance, "ankle", None)
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

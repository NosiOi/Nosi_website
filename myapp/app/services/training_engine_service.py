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
    def build_profile(user):
        """Створює snapshot профілю користувача."""
        return UserProfileSnapshot(
            age=user.age,
            sex=user.sex,
            weight=user.weight,
            height=user.height,
            activity=user.activity,
            goal=user.goal,
            experience=user.experience,
            workouts_per_week=user.workouts_per_week,
            environment=user.environment,
            weak_points=user.weak_points or [],
            strong_points=user.strong_points or []
        )

    @staticmethod
    def generate_plan(user, week=1):
        profile = TrainingEngineService.build_profile(user)
        generator = PlanGenerator(profile)
        return generator.generate(week)

    @staticmethod
    def compute_analytics(performance, recovery):
        strength = StrengthIndex(
            pushups=performance.pushups,
            squats=performance.squats,
            situps=performance.situps,
            weight=performance.weight
        ).score()

        endurance = EnduranceIndex(
            pushups=performance.pushups,
            squats=performance.squats,
            plank_sec=performance.plank_sec,
            weight=performance.weight
        ).score()

        mobility = MobilityIndex(
            hip=performance.hip,
            shoulder=performance.shoulder,
            thoracic=performance.thoracic,
            ankle=performance.ankle
        ).score()

        recovery_score = RecoveryIndex(
            sleep_hours=recovery.sleep,
            stress=recovery.stress,
            soreness=recovery.soreness,
            hydration_liters=recovery.hydration
        ).score()

        fatigue = FatigueModel(
            sleep_hours=recovery.sleep,
            stress=recovery.stress,
            soreness=recovery.soreness,
            training_load=performance.training_load
        ).fatigue_score()

        return {
            "strength": strength,
            "endurance": endurance,
            "mobility": mobility,
            "recovery": recovery_score,
            "fatigue": fatigue
        }

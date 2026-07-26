from myapp.app import db
from myapp.app.models.user import User
from myapp.app.services.recovery.sleep_service import SleepService
from myapp.app.services.recovery.habit_service import HabitService
from myapp.app.services.training_load_service import TrainingLoadService
from myapp.app.services.recovery.constants import (
    SLEEP_BASE_TEEN_MINUTES,
    SLEEP_BASE_ADULT_MINUTES,
    SLEEP_BASE_SENIOR_MINUTES,
    HEAVY_LOAD_THRESHOLD,
    VERY_HEAVY_LOAD_THRESHOLD,
    BEGINNER_SLEEP_BONUS_MINUTES,
    ADVANCED_SLEEP_REDUCTION_MINUTES,
    HEAVY_LOAD_SLEEP_BONUS_MINUTES,
    VERY_HEAVY_LOAD_SLEEP_BONUS_MINUTES,
    SLEEP_DEBT_DAYS,
    SLEEP_DEBT_DIVISOR,
    SLEEP_WEIGHT,
    TRAINING_WEIGHT,
    HABIT_WEIGHT,
    ENERGY_WEIGHT,
)


class RecoveryScoreService:
    def __init__(self):
        self.sleep_service = SleepService()
        self.habit_service = HabitService()
        self.training_load = TrainingLoadService()

    def _get_required_sleep_minutes(self, user_id):
        user = User.query.get(user_id)
        age = self.sleep_service.get_age(user)

        if age < 18:
            base = SLEEP_BASE_TEEN_MINUTES
        elif age <= 64:
            base = SLEEP_BASE_ADULT_MINUTES
        else:
            base = SLEEP_BASE_SENIOR_MINUTES

        load = self.training_load.get_daily_load(user_id)
        level = self.training_load.get_user_level(user_id)

        if load > VERY_HEAVY_LOAD_THRESHOLD:
            base += VERY_HEAVY_LOAD_SLEEP_BONUS_MINUTES
        elif load > HEAVY_LOAD_THRESHOLD:
            base += HEAVY_LOAD_SLEEP_BONUS_MINUTES

        if level == "beginner":
            base += BEGINNER_SLEEP_BONUS_MINUTES
        elif level == "advanced":
            base -= ADVANCED_SLEEP_REDUCTION_MINUTES

        return max(360, min(600, base))

    def _get_sleep_debt(self, user_id, required_minutes):
        entries = self.sleep_service.get_last_days(user_id, SLEEP_DEBT_DAYS)
        if not entries:
            return 0

        total_deficit = 0
        for entry in entries:
            total_deficit += max(0, required_minutes - entry.duration_minutes)

        return total_deficit // SLEEP_DEBT_DAYS

    def calculate_habit_score(self, user_id):
        logs = self.habit_service.get_today_logs(user_id)
        if not logs:
            return 0
        completed = sum(1 for log in logs if log.completed)
        total = len(logs)
        return int((completed / total) * 100)

    def calculate_training_score(self, user_id):
        load = self.training_load.get_daily_load(user_id)

        if load <= 40:
            return 30
        if load <= 80:
            return 60
        if load <= 120:
            return 80
        if load <= 160:
            return 85
        if load <= 200:
            return 70
        return 50

    def calculate_energy_score(self, sleep_score, habit_score):
        base = sleep_score * 0.75 + habit_score * 0.25
        return max(0, min(100, int(base)))

    def calculate_recovery_score(
        self,
        user_id,
        sleep_score,
        habit_score,
        training_score,
        energy_score,
    ):
        required_minutes = self._get_required_sleep_minutes(user_id)
        last_sleep = self.sleep_service.get_last_sleep(user_id)
        slept = last_sleep.duration_minutes if last_sleep else 0

        sleep_component = 0
        if required_minutes > 0:
            sleep_component = max(0, min(100, int((slept / required_minutes) * 100)))

        debt = self._get_sleep_debt(user_id, required_minutes)
        load = self.training_load.get_daily_load(user_id)

        fatigue_penalty = 0
        if load > VERY_HEAVY_LOAD_THRESHOLD:
            fatigue_penalty += 20
        elif load > HEAVY_LOAD_THRESHOLD:
            fatigue_penalty += 10

        fatigue_penalty += debt // SLEEP_DEBT_DIVISOR

        base = int(
            sleep_component * SLEEP_WEIGHT
            + habit_score * HABIT_WEIGHT
            + training_score * TRAINING_WEIGHT
            + energy_score * ENERGY_WEIGHT
        )

        final = max(0, min(100, base - fatigue_penalty))
        return final

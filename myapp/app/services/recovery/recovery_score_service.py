from datetime import date

from myapp.app.models.user import User
from myapp.app.models.recovery.sleep_entry import SleepEntry
from myapp.app.services.recovery.sleep_service import SleepService
from myapp.app.services.recovery.habit_service import HabitService
from myapp.app.services.training_load_service import TrainingLoadService
from myapp.app.services.recovery.constants import (
    SLEEP_BASE_YOUNG_MINUTES,
    SLEEP_BASE_ADULT_MINUTES,
    SLEEP_BASE_SENIOR_MINUTES,
    HEAVY_LOAD_THRESHOLD,
    VERY_HEAVY_LOAD_THRESHOLD,
    HEAVY_LOAD_SLEEP_BONUS_MINUTES,
    VERY_HEAVY_LOAD_SLEEP_BONUS_MINUTES,
    BEGINNER_SLEEP_BONUS_MINUTES,
    ADVANCED_SLEEP_REDUCTION_MINUTES,
    SLEEP_DEBT_DAYS,
    SLEEP_DEBT_DIVISOR_MINUTES,
    RECOVERY_SLEEP_WEIGHT,
    RECOVERY_TRAINING_WEIGHT,
    RECOVERY_HABIT_WEIGHT,
    ENERGY_SLEEP_WEIGHT,
    ENERGY_HABIT_WEIGHT,
)


class RecoveryScoreService:
    def __init__(self):
        self.sleep_service = SleepService()
        self.habit_service = HabitService()
        self.training_load = TrainingLoadService()

    def _get_user(self, user_id):
        return User.query.get(user_id)

    def _required_sleep_minutes(self, user, training_load, user_level):
        age = self.sleep_service._get_age(user)
        if age < 18:
            base = SLEEP_BASE_YOUNG_MINUTES
        elif age <= 64:
            base = SLEEP_BASE_ADULT_MINUTES
        else:
            base = SLEEP_BASE_SENIOR_MINUTES

        if training_load > HEAVY_LOAD_THRESHOLD:
            base += HEAVY_LOAD_SLEEP_BONUS_MINUTES
        if training_load > VERY_HEAVY_LOAD_THRESHOLD:
            base += VERY_HEAVY_LOAD_SLEEP_BONUS_MINUTES

        level = (user_level or "intermediate").lower()
        if level == "beginner":
            base += BEGINNER_SLEEP_BONUS_MINUTES
        elif level == "advanced":
            base -= ADVANCED_SLEEP_REDUCTION_MINUTES

        return base

    def _get_sleep_debt(self, user_id, required_minutes):
        entries = (
            SleepEntry.query.filter_by(user_id=user_id)
            .order_by(SleepEntry.sleep_start.desc())
            .limit(SLEEP_DEBT_DAYS)
            .all()
        )
        if not entries:
            return 0

        total_deficit = 0
        for e in entries:
            slept = e.duration_minutes or 0
            total_deficit += max(0, required_minutes - slept)

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
        if load <= 140:
            return 85
        if load <= 180:
            return 70
        return 50

    def calculate_energy_score(self, user_id, sleep_score, habit_score):
        base = sleep_score * ENERGY_SLEEP_WEIGHT + habit_score * ENERGY_HABIT_WEIGHT
        return max(0, min(100, int(base)))

    def calculate_recovery_score(
        self, user_id, sleep_score, habit_score, training_score
    ):
        user = self._get_user(user_id)
        if not user:
            return 0

        load = self.training_load.get_daily_load(user_id)
        level = self.training_load.get_user_level(user_id)
        required = self._required_sleep_minutes(user, load, level)

        last_sleep = self.sleep_service.get_last_sleep(user_id)
        slept = last_sleep.duration_minutes if last_sleep else 0

        sleep_ratio = 0 if required <= 0 else slept / required
        sleep_component = max(0, min(100, int(sleep_ratio * 100)))

        debt = self._get_sleep_debt(user_id, required)

        fatigue_penalty = 0
        if load > HEAVY_LOAD_THRESHOLD:
            fatigue_penalty += 10
        if load > VERY_HEAVY_LOAD_THRESHOLD:
            fatigue_penalty += 20

        debt_penalty = debt // SLEEP_DEBT_DIVISOR_MINUTES

        base = (
            sleep_component * RECOVERY_SLEEP_WEIGHT
            + habit_score * RECOVERY_HABIT_WEIGHT
            + training_score * RECOVERY_TRAINING_WEIGHT
        )

        score = int(base - fatigue_penalty - debt_penalty)
        return max(0, min(100, score))

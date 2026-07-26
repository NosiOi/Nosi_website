from datetime import date, timedelta

from myapp.app.services.recovery.sleep_service import SleepService
from myapp.app.services.recovery.habit_service import HabitService
from myapp.app.services.training_load_service import TrainingLoadService
from myapp.app.services.recovery.constants import (
    SLEEP_WEIGHT,
    TRAINING_WEIGHT,
    HABIT_WEIGHT,
    ENERGY_WEIGHT,
)

DEFAULT_REQUIRED_SLEEP_MINUTES_TEEN = 540
DEFAULT_REQUIRED_SLEEP_MINUTES_ADULT = 480
DEFAULT_REQUIRED_SLEEP_MINUTES_SENIOR = 450

HEAVY_LOAD_THRESHOLD = 140
VERY_HEAVY_LOAD_THRESHOLD = 180

SLEEP_DEBT_DAYS = 5
SLEEP_DEBT_DIVISOR = 20


class RecoveryScoreService:
    def __init__(self):
        self.sleep_service = SleepService()
        self.habit_service = HabitService()
        self.training_load = TrainingLoadService()

    def _get_age(self, user):
        if not user or not getattr(user, "birth_date", None):
            return 30
        today = date.today()
        return (
            today.year
            - user.birth_date.year
            - ((today.month, today.day) < (user.birth_date.month, user.birth_date.day))
        )

    def _required_sleep(self, age, training_load, user_level):
        if age < 18:
            base = DEFAULT_REQUIRED_SLEEP_MINUTES_TEEN
        elif age <= 64:
            base = DEFAULT_REQUIRED_SLEEP_MINUTES_ADULT
        else:
            base = DEFAULT_REQUIRED_SLEEP_MINUTES_SENIOR

        if training_load > HEAVY_LOAD_THRESHOLD:
            base += 30
        if training_load > VERY_HEAVY_LOAD_THRESHOLD:
            base += 30

        if user_level == "beginner":
            base += 15
        elif user_level == "advanced":
            base -= 10

        return base

    def _get_sleep_debt(self, user_id, age, training_load, user_level):
        entries = self.sleep_service.get_last_days(user_id, SLEEP_DEBT_DAYS)
        if not entries:
            return 0

        required = self._required_sleep(age, training_load, user_level)
        total_deficit = 0

        for entry in entries:
            total_deficit += max(0, required - entry.duration_minutes)

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
        if load < 40:
            return 30
        if load < 80:
            return 60
        if load < 140:
            return 85
        if load < VERY_HEAVY_LOAD_THRESHOLD:
            return 70
        return 50

    def calculate_energy_score(self, sleep_score, habit_score):
        base = sleep_score * 0.75 + habit_score * 0.25
        return max(0, min(100, int(base)))

    def calculate_recovery_score(
        self, user, sleep_score, habit_score, training_score, energy_score
    ):
        user_id = user.id
        load = self.training_load.get_daily_load(user_id)
        level = self.training_load.get_user_level(user_id)
        age = self._get_age(user)

        last_sleep = self.sleep_service.get_last_sleep(user_id)
        slept = last_sleep.duration_minutes if last_sleep else 0
        required = self._required_sleep(age, load, level)

        sleep_factor = 0
        if required > 0:
            sleep_factor = max(0, min(100, int((slept / required) * 100)))

        sleep_debt = self._get_sleep_debt(user_id, age, load, level)

        fatigue_penalty = 0
        if load > HEAVY_LOAD_THRESHOLD:
            fatigue_penalty += 10
        if load > VERY_HEAVY_LOAD_THRESHOLD:
            fatigue_penalty += 20

        sleep_debt_penalty = sleep_debt // SLEEP_DEBT_DIVISOR

        base = int(
            sleep_factor * SLEEP_WEIGHT
            + habit_score * HABIT_WEIGHT
            + training_score * TRAINING_WEIGHT
            + energy_score * ENERGY_WEIGHT
        )

        final = base - fatigue_penalty - sleep_debt_penalty
        return max(0, min(100, final))

from myapp.app.services.recovery.sleep_service import SleepService
from myapp.app.services.recovery.habit_service import HabitService
from myapp.app.services.training_load_service import TrainingLoadService
from myapp.app.services.recovery.constants import (
    SLEEP_BASE_CHILD_MINUTES,
    SLEEP_BASE_ADULT_MINUTES,
    SLEEP_BASE_SENIOR_MINUTES,
    HEAVY_LOAD_THRESHOLD,
    VERY_HEAVY_LOAD_THRESHOLD,
    SLEEP_DEBT_DAYS,
    SLEEP_DEBT_DIVISOR,
    SLEEP_WEIGHT,
    TRAINING_WEIGHT,
    HABIT_WEIGHT,
)


class RecoveryScoreService:
    def __init__(self):
        self.sleep_service = SleepService()
        self.habit_service = HabitService()
        self.training_load = TrainingLoadService()

    def _base_required_sleep_minutes(self, age):
        if age < 18:
            return SLEEP_BASE_CHILD_MINUTES
        if age <= 64:
            return SLEEP_BASE_ADULT_MINUTES
        return SLEEP_BASE_SENIOR_MINUTES

    def _required_sleep_minutes(self, age, training_load, user_level):
        base = self._base_required_sleep_minutes(age)

        if training_load > HEAVY_LOAD_THRESHOLD:
            base += 30
        if training_load > VERY_HEAVY_LOAD_THRESHOLD:
            base += 30

        level = (user_level or "beginner").lower()
        if level == "beginner":
            base += 15
        elif level == "advanced":
            base -= 10
        elif level == "elite":
            base -= 15

        return base

    def _get_sleep_debt(self, user_id, age):
        entries = self.sleep_service.get_last_days(user_id, SLEEP_DEBT_DAYS)
        if not entries:
            return 0

        base_required = self._base_required_sleep_minutes(age)
        total = 0
        for e in entries:
            total += max(0, base_required - (e.duration_minutes or 0))

        return total // max(1, len(entries))

    def calculate_sleep_score(self, user_id):
        sleep = self.sleep_service.get_last_sleep(user_id)
        if not sleep:
            return 0
        user = sleep.user
        age = self.sleep_service.get_age(user)
        return self.sleep_service.calculate_sleep_score(sleep.duration_minutes, age)

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
        return int(sleep_score * 0.75 + habit_score * 0.25)

    def calculate_recovery_score(
        self, user_id, sleep_score, habit_score, training_score
    ):
        last_sleep = self.sleep_service.get_last_sleep(user_id)
        user = last_sleep.user if last_sleep else None
        age = self.sleep_service.get_age(user)

        load = self.training_load.get_daily_load(user_id)
        level = self.training_load.get_user_level(user_id)

        required_today = self._required_sleep_minutes(age, load, level)
        slept_today = last_sleep.duration_minutes if last_sleep else 0

        sleep_ratio = 0
        if required_today > 0 and slept_today > 0:
            sleep_ratio = max(0, min(1.2, slept_today / required_today))
        sleep_component = int(100 * sleep_ratio)

        debt = self._get_sleep_debt(user_id, age)

        fatigue_penalty = 0
        if load > HEAVY_LOAD_THRESHOLD:
            fatigue_penalty += 10
        if load > VERY_HEAVY_LOAD_THRESHOLD:
            fatigue_penalty += 15
        fatigue_penalty += debt // SLEEP_DEBT_DIVISOR

        base = int(
            sleep_score * SLEEP_WEIGHT
            + habit_score * HABIT_WEIGHT
            + training_score * TRAINING_WEIGHT
        )

        combined = int((base + sleep_component) / 2)

        final = max(0, min(100, combined - fatigue_penalty))
        return final

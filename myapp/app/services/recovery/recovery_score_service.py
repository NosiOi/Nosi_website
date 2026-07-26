from typing import Optional

from myapp.app.services.recovery.sleep_service import SleepService
from myapp.app.services.recovery.habit_service import HabitService
from myapp.app.services.training_load_service import TrainingLoadService
from myapp.app.services.recovery.constants import (
    SLEEP_WEIGHT,
    TRAINING_WEIGHT,
    HABIT_WEIGHT,
    TRAINING_LOAD_LOW,
    TRAINING_LOAD_MEDIUM,
    TRAINING_LOAD_HIGH,
    TRAINING_LOAD_VERY_HIGH,
    TRAINING_LOAD_EXTREME,
    SLEEP_DEBT_DAYS,
    SLEEP_DEBT_DIVISOR,
    SLEEP_DEFICIT_DIVISOR,
)


class RecoveryScoreService:
    def __init__(self) -> None:
        self.sleep_service = SleepService()
        self.habit_service = HabitService()
        self.training_load = TrainingLoadService()

    def calculate_sleep_score(self, user_id: int) -> int:
        last_sleep = self.sleep_service.get_last_sleep(user_id)
        if not last_sleep:
            return 0

        user = last_sleep.user
        age = self.sleep_service.get_age(user)
        return self.sleep_service.calculate_sleep_score(
            last_sleep.duration_minutes, age
        )

    def _required_sleep_minutes(
        self,
        age: int,
        training_load: float,
        user_level: str,
    ) -> int:
        if age < 18:
            base = 9 * 60
        elif age <= 64:
            base = 8 * 60
        else:
            base = int(7.5 * 60)

        if training_load >= TRAINING_LOAD_VERY_HIGH:
            base += 60
        elif training_load >= TRAINING_LOAD_HIGH:
            base += 30

        level = (user_level or "beginner").lower()
        if level == "beginner":
            base += 20
        elif level == "advanced":
            base -= 10

        return base

    def _sleep_debt_minutes(
        self,
        user_id: int,
        age: int,
        training_load: float,
        user_level: str,
    ) -> int:
        entries = self.sleep_service.get_last_days(user_id, SLEEP_DEBT_DAYS)
        if not entries:
            return 0

        required = self._required_sleep_minutes(age, training_load, user_level)
        total_deficit = 0

        for e in entries:
            deficit = max(0, required - e.duration_minutes)
            total_deficit += deficit

        return total_deficit

    def calculate_habit_score(self, user_id: int) -> int:
        logs = self.habit_service.get_today_logs(user_id)
        if not logs:
            return 0

        completed = sum(1 for log in logs if log.completed)
        total = len(logs)

        if total == 0:
            return 0

        return int((completed / total) * 100)

    def calculate_training_score(self, user_id: int) -> int:
        load = self.training_load.get_daily_load(user_id)

        if load <= TRAINING_LOAD_LOW:
            return 30
        if load <= TRAINING_LOAD_MEDIUM:
            return 60
        if load <= TRAINING_LOAD_HIGH:
            return 80
        if load <= TRAINING_LOAD_VERY_HIGH:
            return 90
        if load <= TRAINING_LOAD_EXTREME:
            return 70
        return 50

    def calculate_energy_score(
        self,
        sleep_score: int,
        habit_score: int,
    ) -> int:
        return int(sleep_score * 0.75 + habit_score * 0.25)

    def calculate_recovery_score(
        self,
        user_id: int,
        sleep_score: int,
        habit_score: int,
        training_score: int,
    ) -> int:
        last_sleep = self.sleep_service.get_last_sleep(user_id)
        if not last_sleep:
            return 0

        user = last_sleep.user
        age = self.sleep_service.get_age(user)
        level: str = getattr(user, "experience_level", "beginner")
        load = self.training_load.get_daily_load(user_id)

        required_minutes = self._required_sleep_minutes(age, load, level)
        slept_minutes = last_sleep.duration_minutes

        sleep_deficit = max(0, required_minutes - slept_minutes)
        sleep_deficit_penalty = sleep_deficit // SLEEP_DEFICIT_DIVISOR

        debt_minutes = self._sleep_debt_minutes(user_id, age, load, level)
        debt_penalty = debt_minutes // SLEEP_DEBT_DIVISOR

        load_penalty = 0
        if load >= TRAINING_LOAD_VERY_HIGH:
            load_penalty += 15
        elif load >= TRAINING_LOAD_HIGH:
            load_penalty += 10

        base = int(
            sleep_score * SLEEP_WEIGHT
            + training_score * TRAINING_WEIGHT
            + habit_score * HABIT_WEIGHT
        )

        total_penalty = sleep_deficit_penalty + debt_penalty + load_penalty
        final = max(0, min(100, base - total_penalty))

        return final

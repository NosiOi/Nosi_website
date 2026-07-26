from myapp.app.services.recovery.sleep_service import SleepService
from myapp.app.services.recovery.habit_service import HabitService
from myapp.app.services.training_load_service import TrainingLoadService
from myapp.app.services.recovery.constants import (
    SLEEP_DEBT_DAYS,
    SLEEP_DEBT_PENALTY_DIVISOR,
    SLEEP_BASE_TEEN_MINUTES,
    SLEEP_BASE_ADULT_MINUTES,
    SLEEP_BASE_SENIOR_MINUTES,
    TRAINING_LOAD_LOW,
    TRAINING_LOAD_MEDIUM,
    TRAINING_LOAD_HIGH,
    TRAINING_LOAD_OPTIMAL,
    TRAINING_LOAD_HEAVY,
    TRAINING_LOAD_VERY_HEAVY,
    SLEEP_WEIGHT,
    TRAINING_WEIGHT,
    HABIT_WEIGHT,
    ENERGY_WEIGHT,
    ENERGY_SLEEP_WEIGHT,
    ENERGY_HABIT_WEIGHT,
    HEAVY_LOAD_RECOVERY_PENALTY,
    VERY_HEAVY_LOAD_RECOVERY_PENALTY,
)


class RecoveryScoreService:
    def __init__(self):
        self.sleep_service = SleepService()
        self.habit_service = HabitService()
        self.training_load = TrainingLoadService()

    def _required_sleep_minutes(self, age, training_load, user_level):
        if age < 18:
            base = SLEEP_BASE_TEEN_MINUTES
        elif age <= 64:
            base = SLEEP_BASE_ADULT_MINUTES
        else:
            base = SLEEP_BASE_SENIOR_MINUTES

        if training_load >= TRAINING_LOAD_VERY_HEAVY:
            base += 60
        elif training_load >= TRAINING_LOAD_HEAVY:
            base += 30

        level = (user_level or "beginner").lower()
        if level == "beginner":
            base += 20
        elif level in ("advanced", "elite"):
            base -= 10

        return base

    def _sleep_debt_minutes(self, user_id, age, user_level):
        entries = self.sleep_service.get_last_days(user_id, SLEEP_DEBT_DAYS)
        if not entries:
            return 0

        total_deficit = 0
        for e in entries:
            load = self.training_load.get_daily_load_for_date(
                user_id, e.sleep_start.date()
            )
            required = self._required_sleep_minutes(age, load, user_level)
            total_deficit += max(0, required - (e.duration_minutes or 0))

        return total_deficit

    def calculate_sleep_score(self, user_id):
        entry = self.sleep_service.get_last_sleep(user_id)
        if not entry:
            return 0

        user = entry.user
        age = self.sleep_service.get_age(user)
        return self.sleep_service.calculate_sleep_score(entry.duration_minutes, age)

    def calculate_habit_score(self, user_id):
        logs = self.habit_service.get_today_logs(user_id)
        if not logs:
            return 0
        completed = sum(1 for log in logs if log.completed)
        total = len(logs)
        return int((completed / total) * 100)

    def calculate_training_score(self, user_id):
        load = self.training_load.get_daily_load(user_id)

        if load <= TRAINING_LOAD_LOW:
            return 30
        if load <= TRAINING_LOAD_MEDIUM:
            return 60
        if load <= TRAINING_LOAD_HIGH:
            return 80
        if load <= TRAINING_LOAD_OPTIMAL:
            return 90
        if load <= TRAINING_LOAD_VERY_HEAVY:
            return 70
        return 50

    def calculate_energy_score(self, sleep_score, habit_score):
        base = sleep_score * ENERGY_SLEEP_WEIGHT + habit_score * ENERGY_HABIT_WEIGHT
        return int(max(0, min(100, base)))

    def calculate_recovery_score(
        self,
        user_id,
        sleep_score,
        habit_score,
        training_score,
        energy_score,
    ):
        last_sleep = self.sleep_service.get_last_sleep(user_id)
        if last_sleep:
            user = last_sleep.user
            age = self.sleep_service.get_age(user)
        else:
            user = None
            age = 30

        level = getattr(user, "experience", "beginner") if user else "beginner"
        load_today = self.training_load.get_daily_load(user_id)

        required_minutes = self._required_sleep_minutes(age, load_today, level)
        slept_minutes = last_sleep.duration_minutes if last_sleep else 0

        if required_minutes <= 0:
            sleep_component = sleep_score
        else:
            sleep_ratio = max(0.0, min(1.2, slept_minutes / required_minutes))
            sleep_component = int(max(0, min(100, sleep_ratio * 100)))

        debt_minutes = self._sleep_debt_minutes(user_id, age, level)
        debt_penalty = debt_minutes // SLEEP_DEBT_PENALTY_DIVISOR

        load_penalty = 0
        if load_today >= TRAINING_LOAD_VERY_HEAVY:
            load_penalty += VERY_HEAVY_LOAD_RECOVERY_PENALTY
        elif load_today >= TRAINING_LOAD_HEAVY:
            load_penalty += HEAVY_LOAD_RECOVERY_PENALTY

        base = int(
            sleep_component * SLEEP_WEIGHT
            + training_score * TRAINING_WEIGHT
            + habit_score * HABIT_WEIGHT
            + energy_score * ENERGY_WEIGHT
        )

        total_penalty = load_penalty + debt_penalty
        final = max(0, min(100, base - total_penalty))

        return final

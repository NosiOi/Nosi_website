from datetime import date, timedelta

from myapp.app.services.recovery.sleep_service import SleepService
from myapp.app.services.recovery.habit_service import HabitService
from myapp.app.services.training_load_service import TrainingLoadService


class RecoveryScoreService:
    def __init__(self):
        self.sleep_service = SleepService()
        self.habit_service = HabitService()
        self.training_load = TrainingLoadService()

    def _get_sleep_debt(self, user_id):
        load = self.training_load.get_daily_load(user_id)
        level = self.training_load.get_user_level(user_id)
        required = self._required_sleep(load, level)

        entries = self.sleep_service.get_last_days(user_id, 5)
        if not entries:
            return 0

        total = 0
        for e in entries:
            total += max(0, required - e.duration_minutes)

        return total // 5

    def _required_sleep(self, training_load, user_level):
        base = 480

        if training_load > 140:
            base += 30
        if training_load > 180:
            base += 60

        if user_level == "beginner":
            base += 20
        elif user_level == "advanced":
            base -= 10

        return base

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
        if load <= 140:
            return 85
        if load <= 180:
            return 70
        return 50

    def calculate_energy_score(self, user_id, sleep_score, habit_score):
        load = self.training_load.get_daily_load(user_id)

        base = sleep_score * 0.6 + habit_score * 0.25

        fatigue_penalty = 0
        if load > 140:
            fatigue_penalty += 10
        if load > 180:
            fatigue_penalty += 20

        energy = int(base - fatigue_penalty)
        return max(0, min(100, energy))

    def calculate_recovery_score(
        self, user_id, sleep_score, habit_score, training_score, energy_score
    ):
        load = self.training_load.get_daily_load(user_id)
        debt = self._get_sleep_debt(user_id)
        level = self.training_load.get_user_level(user_id)

        required = self._required_sleep(load, level)
        last_sleep = self.sleep_service.get_last_sleep(user_id)
        slept = last_sleep.duration_minutes if last_sleep else 0

        sleep_factor = max(0, min(100, int((slept / required) * 100)))

        penalty = 0
        if load > 180:
            penalty += 20
        elif load > 150:
            penalty += 10
        penalty += debt // 20

        base = int(
            sleep_factor * 0.45
            + habit_score * 0.20
            + training_score * 0.15
            + energy_score * 0.20
        )

        return max(0, min(100, base - penalty))

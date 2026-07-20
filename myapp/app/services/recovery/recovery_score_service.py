from myapp.app.services.recovery.sleep_service import SleepService
from myapp.app.services.recovery.habit_service import HabitService


class RecoveryScoreService:
    def calculate_sleep_score(self, user_id):
        sleep_service = SleepService()
        sleep = sleep_service.get_last_sleep(user_id)
        if not sleep:
            return 0
        return sleep_service.calculate_sleep_score(sleep.duration_minutes)

    def calculate_habit_score(self, user_id):
        logs = HabitService().get_today_logs(user_id)
        if not logs:
            return 0
        completed = sum(1 for log in logs if log.completed)
        total = len(logs)
        return int((completed / total) * 100)

    def calculate_training_score(self, last_training_days):
        if last_training_days == 0:
            return 50
        if last_training_days == 1:
            return 80
        if last_training_days == 2:
            return 100
        return 60

    def calculate_energy_score(self, sleep_score, habit_score, training_score):
        return int(sleep_score * 0.4 + training_score * 0.4 + habit_score * 0.2)

    def calculate_recovery_score(
        self, sleep_score, habit_score, training_score, energy_score
    ):
        return int(
            sleep_score * 0.4
            + habit_score * 0.2
            + training_score * 0.3
            + energy_score * 0.1
        )

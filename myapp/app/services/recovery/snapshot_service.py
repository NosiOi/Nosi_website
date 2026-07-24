from datetime import date
from myapp.app import db
from myapp.app.models.recovery.daily_recovery_snapshot import DailyRecoverySnapshot
from myapp.app.services.recovery.recovery_score_service import RecoveryScoreService
from myapp.app.services.recovery.sleep_service import SleepService


class SnapshotService:
    def __init__(self):
        self.scores = RecoveryScoreService()
        self.sleep_service = SleepService()

    def update_snapshot(
        self,
        snapshot,
        sleep_data,
        habit_score,
        training_score,
        energy_score,
        recovery_score,
    ):
        snapshot.sleep_score = sleep_data["sleep_score"]
        snapshot.sleep_duration_minutes = sleep_data["duration"]
        snapshot.sleep_start = sleep_data["start"]
        snapshot.sleep_end = sleep_data["end"]

        snapshot.habit_score = habit_score
        snapshot.training_score = training_score
        snapshot.energy_score = energy_score
        snapshot.recovery_score = recovery_score

    def generate_snapshot(self, user_id, last_training_days):
        today = date.today()

        sleep_entry = self.sleep_service.get_last_sleep(user_id)
        sleep_data = self.sleep_service.get_sleep_data(sleep_entry)

        habit_score = self.scores.calculate_habit_score(user_id)
        training_score = self.scores.calculate_training_score(last_training_days)
        energy_score = self.scores.calculate_energy_score(
            sleep_data["sleep_score"], habit_score, training_score
        )
        recovery_score = self.scores.calculate_recovery_score(
            sleep_data["sleep_score"], habit_score, training_score, energy_score
        )

        snapshot = DailyRecoverySnapshot.query.filter_by(
            user_id=user_id, date=today
        ).first()

        if snapshot:
            self.update_snapshot(
                snapshot,
                sleep_data,
                habit_score,
                training_score,
                energy_score,
                recovery_score,
            )
        else:
            snapshot = DailyRecoverySnapshot(
                user_id=user_id,
                date=today,
                sleep_score=sleep_data["sleep_score"],
                sleep_duration_minutes=sleep_data["duration"],
                sleep_start=sleep_data["start"],
                sleep_end=sleep_data["end"],
                habit_score=habit_score,
                training_score=training_score,
                energy_score=energy_score,
                recovery_score=recovery_score,
            )
            db.session.add(snapshot)

        db.session.commit()
        return snapshot

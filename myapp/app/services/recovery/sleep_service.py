from datetime import datetime, timedelta, timezone
from myapp.app import db
from myapp.app.models.recovery.sleep_entry import SleepEntry
from myapp.app.services.recovery.constants import SLEEP_EXCELLENT, SLEEP_GOOD, SLEEP_OK


class SleepService:
    def calculate_duration(self, start, end):
        return int((end - start).total_seconds() // 60)

    def calculate_sleep_score(self, duration):
        if duration >= SLEEP_EXCELLENT:
            return 100
        if duration >= SLEEP_GOOD:
            return 85
        if duration >= SLEEP_OK:
            return 70
        if duration >= 300:
            return 50
        return 30

    def add_sleep(self, user_id, sleep_start, sleep_end):
        duration = self.calculate_duration(sleep_start, sleep_end)
        score = self.calculate_sleep_score(duration)
        entry = SleepEntry(
            user_id=user_id,
            sleep_start=sleep_start,
            sleep_end=sleep_end,
            duration_minutes=duration,
            quality_score=score,
        )
        db.session.add(entry)
        db.session.commit()
        return entry

    def get_last_sleep(self, user_id):
        return (
            SleepEntry.query.filter_by(user_id=user_id)
            .order_by(SleepEntry.sleep_start.desc())
            .first()
        )

    def get_sleep_history(self, user_id, days=30):
        cutoff = datetime.now(timezone.utc) - timedelta(days=days)
        return (
            SleepEntry.query.filter(
                SleepEntry.user_id == user_id, SleepEntry.sleep_start >= cutoff
            )
            .order_by(SleepEntry.sleep_start.desc())
            .all()
        )

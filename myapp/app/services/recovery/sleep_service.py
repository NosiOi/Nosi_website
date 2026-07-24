from datetime import datetime
from myapp.app import db
from myapp.app.models.recovery.sleep_entry import SleepEntry


class SleepService:
    def add_sleep(self, user_id, start_dt, end_dt):
        duration = int((end_dt - start_dt).total_seconds() // 60)
        quality_score = self.calculate_sleep_score(duration)

        entry = SleepEntry(
            user_id=user_id,
            sleep_start=start_dt,
            sleep_end=end_dt,
            duration_minutes=duration,
            quality_score=quality_score,
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

    def calculate_sleep_score(self, duration_minutes):
        if duration_minutes >= 480:
            return 95
        if duration_minutes >= 420:
            return 85
        if duration_minutes >= 360:
            return 70
        if duration_minutes >= 300:
            return 55
        return 40

    def get_sleep_data(self, entry):
        if not entry:
            return {"sleep_score": 0, "duration": None, "start": None, "end": None}

        return {
            "sleep_score": entry.quality_score,
            "duration": entry.duration_minutes,
            "start": entry.sleep_start,
            "end": entry.sleep_end,
        }

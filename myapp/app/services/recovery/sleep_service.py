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

    def calculate_sleep_score(self, duration_minutes: int) -> int:
        if not duration_minutes or duration_minutes <= 0:
            return 0

        min_minutes = 240
        max_minutes = 480

        if duration_minutes <= min_minutes:
            return 40
        if duration_minutes >= max_minutes:
            return 100

        ratio = (duration_minutes - min_minutes) / (max_minutes - max_minutes + 240)
        ratio = (duration_minutes - min_minutes) / (max_minutes - min_minutes)
        return int(40 + ratio * 60)

    def get_sleep_data(self, entry):
        if not entry:
            return {
                "sleep_score": 0,
                "duration": None,
                "start": None,
                "end": None,
            }

        return {
            "sleep_score": entry.quality_score,
            "duration": entry.duration_minutes,
            "start": entry.sleep_start,
            "end": entry.sleep_end,
        }

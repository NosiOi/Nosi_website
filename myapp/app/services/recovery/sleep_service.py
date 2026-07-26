from datetime import date, timedelta

from myapp.app import db
from myapp.app.models.recovery.sleep_entry import SleepEntry
from myapp.app.models.user import User


class SleepService:
    def add_sleep(self, user_id, sleep_start, sleep_end):
        duration = sleep_end - sleep_start
        duration_minutes = int(duration.total_seconds() // 60)

        user = User.query.get(user_id)
        age = self.get_age(user)
        sleep_score = self.calculate_sleep_score(duration_minutes, age)

        entry = SleepEntry(
            user_id=user_id,
            sleep_start=sleep_start,
            sleep_end=sleep_end,
            duration_minutes=duration_minutes,
            quality_score=sleep_score,
        )

        db.session.add(entry)
        db.session.commit()

        return entry

    def get_age(self, user):
        if not user or not getattr(user, "birth_date", None):
            return 30
        today = date.today()
        return (
            today.year
            - user.birth_date.year
            - ((today.month, today.day) < (user.birth_date.month, user.birth_date.day))
        )

    def calculate_sleep_score(self, duration_minutes, age):
        hours = duration_minutes / 60.0

        if age < 18:
            target_min = 8.0
            target_max = 10.0
        elif age <= 64:
            target_min = 7.0
            target_max = 9.0
        else:
            target_min = 7.0
            target_max = 8.0

        if hours < 4.0:
            return 30
        if hours > 11.0:
            return 40

        if target_min <= hours <= target_max:
            center = (target_min + target_max) / 2.0
            diff = abs(hours - center)
            return max(90, int(100 - diff * 4))

        if hours < target_min:
            deficit = target_min - hours
            penalty = deficit * 18
            return max(35, int(95 - penalty))

        surplus = hours - target_max
        penalty = surplus * 12
        return max(45, int(95 - penalty))

    def get_last_sleep(self, user_id):
        return (
            SleepEntry.query.filter_by(user_id=user_id)
            .order_by(SleepEntry.sleep_start.desc())
            .first()
        )

    def get_last_days(self, user_id, days):
        if days <= 0:
            return []
        today = date.today()
        start_date = today - timedelta(days=days - 1)
        return (
            SleepEntry.query.filter(
                SleepEntry.user_id == user_id,
                SleepEntry.sleep_start >= start_date,
            )
            .order_by(SleepEntry.sleep_start.desc())
            .all()
        )

    def get_sleep_data(self, entry):
        if not entry:
            return {
                "sleep_score": 0,
                "duration": 0,
                "start": None,
                "end": None,
            }
        return {
            "sleep_score": entry.quality_score or 0,
            "duration": entry.duration_minutes or 0,
            "start": entry.sleep_start,
            "end": entry.sleep_end,
        }

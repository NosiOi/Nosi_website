from datetime import datetime, date, timedelta
from typing import Optional, List

from myapp.app import db
from myapp.app.models.recovery.sleep_entry import SleepEntry
from myapp.app.models.user import User

# Sleep scoring constants
SLEEP_MIN_HOURS = 4.0
SLEEP_MAX_HOURS = 11.0

SLEEP_SCORE_MIN = 40
SLEEP_SCORE_MAX = 100

SLEEP_DEFICIT_PENALTY_PER_HOUR = 18
SLEEP_SURPLUS_PENALTY_PER_HOUR = 12


class SleepService:
    def add_sleep(
        self,
        user_id: int,
        sleep_start: datetime,
        sleep_end: datetime,
    ) -> SleepEntry:
        duration = sleep_end - sleep_start
        duration_minutes = int(duration.total_seconds() // 60)

        user: Optional[User] = db.session.get(User, user_id)
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

    def get_age(self, user: Optional[User]) -> int:
        if not user or not getattr(user, "birth_date", None):
            return 30

        today: date = date.today()
        birth: date = user.birth_date

        return (
            today.year
            - birth.year
            - ((today.month, today.day) < (birth.month, birth.day))
        )

    def calculate_sleep_score(self, duration_minutes: int, age: int) -> int:
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

        if hours < SLEEP_MIN_HOURS:
            return 30
        if hours > SLEEP_MAX_HOURS:
            return 40

        if target_min <= hours <= target_max:
            # Slight bonus for being close to the middle of the range
            center = (target_min + target_max) / 2.0
            distance = abs(hours - center)
            bonus = max(0, int(5 - distance * 2))
            return min(SLEEP_SCORE_MAX, 95 + bonus)

        if hours < target_min:
            deficit = target_min - hours
            penalty = deficit * SLEEP_DEFICIT_PENALTY_PER_HOUR
            return max(SLEEP_SCORE_MIN, int(95 - penalty))

        surplus = hours - target_max
        penalty = surplus * SLEEP_SURPLUS_PENALTY_PER_HOUR
        return max(45, int(95 - penalty))

    def get_last_sleep(self, user_id: int) -> Optional[SleepEntry]:
        return (
            SleepEntry.query.filter_by(user_id=user_id)
            .order_by(SleepEntry.sleep_end.desc())
            .first()
        )

    def get_last_days(self, user_id: int, days: int) -> List[SleepEntry]:
        cutoff = datetime.utcnow() - timedelta(days=days)
        return (
            SleepEntry.query.filter(
                SleepEntry.user_id == user_id,
                SleepEntry.sleep_end >= cutoff,
            )
            .order_by(SleepEntry.sleep_end.desc())
            .all()
        )

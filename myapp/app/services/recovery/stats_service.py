from datetime import date
from typing import List, Dict, Any, Optional

from myapp.app.models.recovery.daily_recovery_snapshot import DailyRecoverySnapshot


class StatsService:
    def get_daily_snapshot(
        self,
        user_id: int,
        day: date,
    ) -> Optional[DailyRecoverySnapshot]:
        return DailyRecoverySnapshot.query.filter_by(
            user_id=user_id,
            date=day,
        ).first()

    def get_last_snapshot(self, user_id: int) -> Optional[DailyRecoverySnapshot]:
        return (
            DailyRecoverySnapshot.query.filter_by(user_id=user_id)
            .order_by(DailyRecoverySnapshot.date.desc())
            .first()
        )

    def get_heatmap(self, user_id: int, year: int) -> List[Dict[str, Any]]:
        start = date(year, 1, 1)
        end = date(year, 12, 31)

        snapshots = (
            DailyRecoverySnapshot.query.filter(
                DailyRecoverySnapshot.user_id == user_id,
                DailyRecoverySnapshot.date >= start,
                DailyRecoverySnapshot.date <= end,
            )
            .order_by(DailyRecoverySnapshot.date.asc())
            .all()
        )

        result: List[Dict[str, Any]] = []

        for s in snapshots:
            score = s.recovery_score or 0
            if score >= 85:
                level = 4
            elif score >= 70:
                level = 3
            elif score >= 50:
                level = 2
            elif score >= 30:
                level = 1
            else:
                level = 0

            result.append(
                {
                    "date": s.date,
                    "recovery_score": score,
                    "level": level,
                }
            )

        return result

    def get_weekly_stats(self, user_id: int) -> Optional[int]:
        cutoff = date.today().fromordinal(date.today().toordinal() - 7)
        snapshots = DailyRecoverySnapshot.query.filter(
            DailyRecoverySnapshot.user_id == user_id,
            DailyRecoverySnapshot.date >= cutoff,
        ).all()

        if not snapshots:
            return None

        return round(sum(s.recovery_score for s in snapshots) / len(snapshots))

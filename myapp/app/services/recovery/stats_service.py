from datetime import date, timedelta
from typing import List, Dict

from myapp.app.models.recovery.daily_recovery_snapshot import DailyRecoverySnapshot


class StatsService:
    """Weekly recovery statistics."""

    def get_weekly_stats(self, user_id: int) -> Dict:
        today = date.today()
        start = today - timedelta(days=6)

        snapshots = (
            DailyRecoverySnapshot.query.filter(
                DailyRecoverySnapshot.user_id == user_id,
                DailyRecoverySnapshot.date >= start,
                DailyRecoverySnapshot.date <= today,
            )
            .order_by(DailyRecoverySnapshot.date.asc())
            .all()
        )

        total = sum((s.recovery_score or 0) for s in snapshots)
        count = len(snapshots)
        avg = int(total / count) if count else 0

        return {
            "average_recovery": avg,
            "days": [
                {"date": s.date.isoformat(), "recovery_score": s.recovery_score or 0}
                for s in snapshots
            ],
        }

from datetime import date, timedelta
from myapp.app.models.recovery.daily_recovery_snapshot import DailyRecoverySnapshot


class StatsService:
    def get_daily_snapshot(self, user_id, day):
        return DailyRecoverySnapshot.query.filter_by(user_id=user_id, date=day).first()

    def get_last_snapshot(self, user_id):
        return (
            DailyRecoverySnapshot.query.filter_by(user_id=user_id)
            .order_by(DailyRecoverySnapshot.date.desc())
            .first()
        )

    def get_heatmap(self, user_id, days=30):
        cutoff = date.today() - timedelta(days=days)
        return (
            DailyRecoverySnapshot.query.filter(
                DailyRecoverySnapshot.user_id == user_id,
                DailyRecoverySnapshot.date >= cutoff,
            )
            .order_by(DailyRecoverySnapshot.date.asc())
            .all()
        )

    def get_weekly_stats(self, user_id):
        cutoff = date.today() - timedelta(days=7)
        snapshots = DailyRecoverySnapshot.query.filter(
            DailyRecoverySnapshot.user_id == user_id,
            DailyRecoverySnapshot.date >= cutoff,
        ).all()
        if not snapshots:
            return None
        return round(sum(s.recovery_score for s in snapshots) / len(snapshots))

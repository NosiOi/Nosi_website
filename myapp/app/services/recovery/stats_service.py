from datetime import date
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

    def get_heatmap(self, user_id, year):
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

        for s in snapshots:
            score = s.recovery_score or 0
            if score >= 85:
                s.level = 4
            elif score >= 70:
                s.level = 3
            elif score >= 50:
                s.level = 2
            elif score >= 30:
                s.level = 1
            else:
                s.level = 0

        return snapshots

    def get_weekly_stats(self, user_id):
        cutoff = date.today().fromordinal(date.today().toordinal() - 7)
        snapshots = DailyRecoverySnapshot.query.filter(
            DailyRecoverySnapshot.user_id == user_id,
            DailyRecoverySnapshot.date >= cutoff,
        ).all()

        if not snapshots:
            return None

        return round(sum(s.recovery_score for s in snapshots) / len(snapshots))

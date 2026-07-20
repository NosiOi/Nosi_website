from datetime import datetime
from myapp.app import db


class RecoveryHabitLog(db.Model):
    __tablename__ = "recovery_habit_logs"

    id = db.Column(db.Integer, primary_key=True)

    user_habit_id = db.Column(
        db.Integer, db.ForeignKey("user_recovery_habits.id"), nullable=False
    )
    user_habit = db.relationship(
        "UserRecoveryHabit", back_populates="logs", cascade="all, delete-orphan"
    )

    date = db.Column(db.Date, nullable=False)
    completed = db.Column(db.Boolean, default=False, nullable=False)
    completed_at = db.Column(db.DateTime, nullable=True)

    created_at = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)

    __table_args__ = (
        db.UniqueConstraint("user_habit_id", "date", name="uq_habit_day"),
    )

from sqlalchemy.sql import func
from myapp.app import db


class RecoveryHabitLog(db.Model):
    __tablename__ = "recovery_habit_logs"

    id = db.Column(db.Integer, primary_key=True)

    user_habit_id = db.Column(
        db.Integer,
        db.ForeignKey("user_recovery_habits.id", ondelete="CASCADE"),
        nullable=False,
    )
    user_habit = db.relationship("UserRecoveryHabit", back_populates="logs")

    date = db.Column(db.Date, nullable=False)
    completed = db.Column(db.Boolean, nullable=False, default=False)
    completed_at = db.Column(db.DateTime(timezone=True), nullable=True)

    created_at = db.Column(
        db.DateTime(timezone=True), server_default=func.now(), nullable=False
    )

    __table_args__ = (
        db.UniqueConstraint("user_habit_id", "date", name="uq_habit_day"),
        db.Index("idx_habit_log", "user_habit_id", "date"),
    )

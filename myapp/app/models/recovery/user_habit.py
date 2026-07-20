from sqlalchemy.sql import func
from myapp.app import db


class UserRecoveryHabit(db.Model):
    __tablename__ = "user_recovery_habits"

    id = db.Column(db.Integer, primary_key=True)

    user_id = db.Column(
        db.Integer, db.ForeignKey("users.id", ondelete="CASCADE"), nullable=False
    )
    user = db.relationship("User", back_populates="recovery_habits")

    habit_id = db.Column(
        db.Integer,
        db.ForeignKey("recovery_habits.id", ondelete="CASCADE"),
        nullable=False,
    )
    habit = db.relationship("RecoveryHabit", back_populates="user_habits")

    created_at = db.Column(
        db.DateTime(timezone=True), server_default=func.now(), nullable=False
    )
    updated_at = db.Column(
        db.DateTime(timezone=True),
        server_default=func.now(),
        onupdate=func.now(),
        nullable=False,
    )

    is_active = db.Column(db.Boolean, nullable=False, default=True)

    logs = db.relationship(
        "RecoveryHabitLog", back_populates="user_habit", cascade="all, delete-orphan"
    )

    __table_args__ = (
        db.UniqueConstraint("user_id", "habit_id", name="uq_user_habit"),
        db.Index("idx_user_habits", "user_id", "is_active"),
    )

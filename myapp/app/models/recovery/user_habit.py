from datetime import datetime
from myapp.app import db


class UserRecoveryHabit(db.Model):
    __tablename__ = "user_recovery_habits"

    id = db.Column(db.Integer, primary_key=True)

    user_id = db.Column(db.Integer, db.ForeignKey("users.id"), nullable=False)
    user = db.relationship("User", back_populates="recovery_habits")

    habit_id = db.Column(
        db.Integer, db.ForeignKey("recovery_habits.id"), nullable=False
    )
    habit = db.relationship("RecoveryHabit", back_populates="user_habits")

    created_at = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)
    is_active = db.Column(db.Boolean, default=True, nullable=False)

    logs = db.relationship("RecoveryHabitLog", back_populates="user_habit")

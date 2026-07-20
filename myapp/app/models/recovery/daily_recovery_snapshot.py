from sqlalchemy.sql import func
from myapp.app import db
from sqlalchemy import CheckConstraint


class DailyRecoverySnapshot(db.Model):
    __tablename__ = "daily_recovery_snapshot"

    id = db.Column(db.Integer, primary_key=True)

    user_id = db.Column(
        db.Integer, db.ForeignKey("users.id", ondelete="CASCADE"), nullable=False
    )
    user = db.relationship("User", back_populates="daily_recovery")

    date = db.Column(db.Date, nullable=False)

    sleep_score = db.Column(db.Integer, nullable=False, default=0)
    habit_score = db.Column(db.Integer, nullable=False, default=0)
    training_score = db.Column(db.Integer, nullable=False, default=0)
    energy_score = db.Column(db.Integer, nullable=False, default=0)
    recovery_score = db.Column(db.Integer, nullable=False, default=0)

    created_at = db.Column(
        db.DateTime(timezone=True), server_default=func.now(), nullable=False
    )
    updated_at = db.Column(
        db.DateTime(timezone=True),
        server_default=func.now(),
        onupdate=func.now(),
        nullable=False,
    )

    __table_args__ = (
        db.UniqueConstraint("user_id", "date", name="uq_daily_recovery"),
        db.Index("idx_daily_recovery", "user_id", "date"),
        CheckConstraint("sleep_score BETWEEN 0 AND 100", name="ck_sleep_score"),
        CheckConstraint("habit_score BETWEEN 0 AND 100", name="ck_habit_score"),
        CheckConstraint("training_score BETWEEN 0 AND 100", name="ck_training_score"),
        CheckConstraint("energy_score BETWEEN 0 AND 100", name="ck_energy_score"),
        CheckConstraint("recovery_score BETWEEN 0 AND 100", name="ck_recovery_score"),
    )

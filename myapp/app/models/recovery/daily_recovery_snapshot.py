from sqlalchemy.sql import func
from myapp.app import db
from sqlalchemy import CheckConstraint


class DailyRecoverySnapshot(db.Model):
    __tablename__ = "recovery_daily_snapshots"

    id = db.Column(db.Integer, primary_key=True)

    user_id = db.Column(db.Integer, db.ForeignKey("users.id"), nullable=False)
    date = db.Column(db.Date, nullable=False, index=True)

    sleep_score = db.Column(db.Integer, nullable=False)
    habit_score = db.Column(db.Integer, nullable=False)
    training_score = db.Column(db.Integer, nullable=False)
    energy_score = db.Column(db.Integer, nullable=False)
    recovery_score = db.Column(db.Integer, nullable=False)

    created_at = db.Column(db.DateTime(timezone=True), server_default=func.now())
    updated_at = db.Column(
        db.DateTime(timezone=True), server_default=func.now(), onupdate=func.now()
    )

    user = db.relationship("User", back_populates="daily_recovery_snapshots")

    def to_dict(self):
        return {
            "id": self.id,
            "date": self.date.isoformat(),
            "sleep_score": self.sleep_score,
            "habit_score": self.habit_score,
            "training_score": self.training_score,
            "energy_score": self.energy_score,
            "recovery_score": self.recovery_score,
            "updated_at": self.updated_at.isoformat() if self.updated_at else None,
        }

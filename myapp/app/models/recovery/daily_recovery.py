from datetime import datetime
from myapp.app import db


class DailyRecovery(db.Model):
    __tablename__ = "daily_recovery"

    id = db.Column(db.Integer, primary_key=True)

    user_id = db.Column(db.Integer, db.ForeignKey("users.id"), nullable=False)
    user = db.relationship("User", back_populates="daily_recovery")

    date = db.Column(db.Date, nullable=False)

    sleep_score = db.Column(db.Integer, nullable=True)
    habit_score = db.Column(db.Integer, nullable=True)
    training_score = db.Column(db.Integer, nullable=True)
    recovery_score = db.Column(db.Integer, nullable=True)

    created_at = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)

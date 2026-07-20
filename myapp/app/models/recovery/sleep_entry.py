from datetime import datetime
from myapp.app import db


class SleepEntry(db.Model):
    __tablename__ = "recovery_sleep_entries"

    id = db.Column(db.Integer, primary_key=True)

    user_id = db.Column(db.Integer, db.ForeignKey("users.id"), nullable=False)
    user = db.relationship("User", back_populates="sleep_entries")

    sleep_start = db.Column(db.DateTime, nullable=False)
    sleep_end = db.Column(db.DateTime, nullable=False)

    duration_minutes = db.Column(db.Integer, nullable=False)
    quality_score = db.Column(db.Integer, nullable=True)

    created_at = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)
    updated_at = db.Column(
        db.DateTime,
        default=datetime.utcnow,
        onupdate=datetime.utcnow,
        nullable=False,
    )

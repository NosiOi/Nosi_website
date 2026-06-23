from datetime import datetime
from typing import Dict
from myapp.app import db
from myapp.app.training_engine.models.training_day import TrainingDay


class TrainingPlan(db.Model):
    __tablename__ = "te_training_plans"

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(
        db.Integer, db.ForeignKey("users.id"), nullable=False, index=True
    )
    name = db.Column(db.String(250), nullable=False, default="Plan")
    is_active = db.Column(db.Boolean, default=False, nullable=False)

    created_at = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)
    updated_at = db.Column(
        db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False
    )

    owner = db.relationship("User", back_populates="training_plans", lazy="joined")

    def __init__(self, user_id: int, name: str = "Plan", is_active: bool = False):
        self.user_id = user_id
        self.name = name
        self.is_active = is_active
        self._days: Dict[str, TrainingDay] = {}

    @property
    def days(self) -> Dict[str, TrainingDay]:
        return self._days

    @days.setter
    def days(self, value: Dict[str, TrainingDay]):
        self._days = value

    def add_day(self, key: str, day: TrainingDay):
        self._days[key] = day

    def to_dict(self) -> Dict:
        return {
            "id": self.id,
            "user_id": self.user_id,
            "name": self.name,
            "is_active": bool(self.is_active),
            "days": {
                key: day.to_dict() if hasattr(day, "to_dict") else day
                for key, day in self._days.items()
            },
            "created_at": self.created_at.isoformat() if self.created_at else None,
            "updated_at": self.updated_at.isoformat() if self.updated_at else None,
        }

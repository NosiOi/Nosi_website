from datetime import datetime
from typing import Dict
from myapp.app import db
from sqlalchemy.dialects.postgresql import JSONB
from myapp.app.training_engine.models.training_day import TrainingDay


class TrainingPlan(db.Model):
    __tablename__ = "te_training_plans"

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(
        db.Integer, db.ForeignKey("users.id"), nullable=False, index=True
    )
    name = db.Column(db.String(250), nullable=False, default="Plan")
    is_active = db.Column(db.Boolean, default=False, nullable=False)

    days = db.Column(JSONB, nullable=False, default=dict)

    created_at = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)
    updated_at = db.Column(
        db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False
    )

    owner = db.relationship("User", back_populates="training_plans", lazy="joined")

    def add_day(self, key: str, day: TrainingDay):
        """
        Додає день у JSON форматі.
        """
        if not self.days:
            self.days = {}

        self.days[key] = day.to_dict()

    def to_dict(self) -> Dict:
        """
        Повертає повністю готовий словник для фронтенду.
        """
        return {
            "id": self.id,
            "user_id": self.user_id,
            "name": self.name,
            "is_active": bool(self.is_active),
            "days": self.days or {},
            "created_at": self.created_at.isoformat() if self.created_at else None,
            "updated_at": self.updated_at.isoformat() if self.updated_at else None,
        }

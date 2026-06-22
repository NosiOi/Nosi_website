from datetime import datetime
from typing import Any, Dict

from myapp.app import db
from myapp.app.training_engine.models.training_day import TrainingDay
import json


class TrainingPlan(db.Model):
    __tablename__ = "te_training_plans"

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey("users.id"), nullable=False, index=True)
    name = db.Column(db.String(250), nullable=False, default="Plan")
    meta = db.Column(db.Text, nullable=True)
    is_active = db.Column(db.Boolean, default=False, nullable=False)

    created_at = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)

    owner = db.relationship("User", back_populates="training_plans", lazy="joined")

    def get_meta(self) -> Dict[str, Any]:
        try:
            return json.loads(self.meta) if self.meta else {}
        except Exception:
            return {}

    def set_meta(self, meta_obj: Dict[str, Any]) -> None:
        self.meta = json.dumps(meta_obj)

    @property
    def days(self):
        meta = self.get_meta()
        days = meta.get("days", {})

        normalized = {}
        for key, raw in days.items():
            if isinstance(raw, dict):
                normalized[key] = TrainingDay.from_dict(raw)
            else:
                normalized[key] = raw

        return normalized

    def add_day(self, key: str, day: TrainingDay):
        meta = self.get_meta()
        days = meta.get("days", {})
        days[key] = day.to_dict()
        meta["days"] = days
        self.set_meta(meta)

    def to_dict(self) -> Dict[str, Any]:
        return {
            "id": self.id,
            "user_id": self.user_id,
            "name": self.name,
            "meta": self.get_meta(),
            "is_active": bool(self.is_active),
            "created_at": self.created_at.isoformat() if self.created_at else None,
            "updated_at": self.updated_at.isoformat() if self.updated_at else None,
        }

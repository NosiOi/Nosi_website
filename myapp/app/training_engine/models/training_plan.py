from dataclasses import dataclass, field
from datetime import datetime
from typing import Any, Dict, List, Optional
import json

from myapp.app import db
from myapp.app.training_engine.models.training_day import TrainingDay


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

    def __init__(self, *args, **kwargs):
        # allow legacy/test kwargs (goal, experience, workouts_per_week) as plain attributes
        db_fields = {"id", "user_id", "name", "meta", "is_active", "created_at", "updated_at"}
        init_kwargs = {}
        for k in list(kwargs.keys()):
            if k in db_fields:
                init_kwargs[k] = kwargs.pop(k)
        super().__init__(**init_kwargs)
        for k, v in kwargs.items():
            setattr(self, k, v)

    def get_meta(self) -> Dict[str, Any]:
        try:
            return json.loads(self.meta) if self.meta else {}
        except Exception:
            return {}

    def set_meta(self, meta_obj: Dict[str, Any]) -> None:
        self.meta = json.dumps(meta_obj)

    @property
    def days(self):
        # Return meta['days'] as dict (compat with tests that expect plan.days).
        meta = self.get_meta()
        days = meta.get("days", {})
        if isinstance(days, dict):
            return days
        # if stored as list, convert to dict with indices or day_name
        if isinstance(days, list):
            out = {}
            for i, d in enumerate(days):
                key = d.get("day_name") or d.get("name") or str(i)
                out[key] = d
            return out
        return {}


    def add_day(self, key: str, day: TrainingDay):
        """
        Add or replace a day in plan.meta under 'days'.
        Keeps 'days' as dict keyed by provided key for compatibility with tests.
        """
        meta = self.get_meta()
        days = meta.get("days", {})
        if not isinstance(days, dict):
            days = {}
        days[key] = day.to_dict() if hasattr(day, "to_dict") else dict(day)
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

    def __repr__(self) -> str:
        return f"<TrainingPlan id={self.id} name={self.name}>"

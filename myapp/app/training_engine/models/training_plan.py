from dataclasses import dataclass, field
from datetime import datetime
from typing import Any, Dict, List, Optional

from myapp.app import db


@dataclass
class TrainingDay:
    """
    Lightweight value object representing a single training day inside a plan.
    """
    name: Optional[str] = None
    exercises: List[Dict[str, Any]] = field(default_factory=list)

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "TrainingDay":
        name = data.get("name")
        exercises = data.get("exercises", []) or []
        return cls(name=name, exercises=list(exercises))

    def to_dict(self) -> Dict[str, Any]:
        return {"name": self.name, "exercises": list(self.exercises)}


class TrainingPlan(db.Model):
    __tablename__ = "te_training_plans"

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey("users.id"), nullable=False, index=True)
    name = db.Column(db.String(250), nullable=False)
    meta = db.Column(db.Text, nullable=True)  # JSON blob describing days, structure, etc.
    is_active = db.Column(db.Boolean, default=False, nullable=False)

    created_at = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)

    def get_meta(self) -> Dict[str, Any]:
        import json
        try:
            return json.loads(self.meta) if self.meta else {}
        except Exception:
            return {}

    def set_meta(self, meta_obj: Dict[str, Any]) -> None:
        import json
        self.meta = json.dumps(meta_obj)

    def get_days(self) -> List[TrainingDay]:
        meta = self.get_meta()
        days = meta.get("days", {})
        result: List[TrainingDay] = []
        if isinstance(days, dict):
            for k in sorted(days.keys()):
                d = days.get(k) or {}
                result.append(TrainingDay.from_dict(d))
        elif isinstance(days, list):
            for d in days:
                result.append(TrainingDay.from_dict(d or {}))
        return result

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

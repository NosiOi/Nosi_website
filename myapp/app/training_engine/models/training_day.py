from datetime import datetime
import json
from myapp.app import db

class TrainingDay(db.Model):
    __tablename__ = "te_training_days"

    id = db.Column(db.Integer, primary_key=True)
    plan_id = db.Column(db.Integer, nullable=True, index=True)
    name = db.Column(db.String(120), nullable=False)
    meta = db.Column(db.Text, nullable=True)  # JSON: exercises, sets, reps
    focus = db.Column(db.String(120), nullable=True, default="general")
    environment = db.Column(db.String(50), nullable=True, default="gym")
    created_at = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)

    def to_dict(self):
        try:
            meta = json.loads(self.meta) if self.meta else {}
        except Exception:
            meta = {}
        return {
            "id": self.id,
            "name": self.name,
            "meta": meta,
            "focus": self.focus,
            "environment": self.environment
        }

    def add_exercise(self, exercise_id, sets=3, reps="8"):
        try:
            meta = json.loads(self.meta) if self.meta else {"exercises": []}
        except Exception:
            meta = {"exercises": []}
        meta.setdefault("exercises", []).append({"id": exercise_id, "sets": sets, "reps": reps})
        self.meta = json.dumps(meta)

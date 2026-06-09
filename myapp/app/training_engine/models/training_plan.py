from datetime import datetime
from myapp.app import db


class TrainingPlan(db.Model):
    __tablename__ = "te_training_plans"

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, nullable=False, index=True)
    name = db.Column(db.String(250), nullable=False)
    meta = db.Column(db.Text, nullable=True)  # JSON: days, exercises, order
    is_active = db.Column(db.Boolean, default=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)

    def to_dict(self):
        return {
            "id": self.id,
            "user_id": self.user_id,
            "name": self.name,
            "meta": self.meta,
            "is_active": self.is_active
        }

    def __repr__(self):
        return f"<TrainingPlan id={self.id} name={self.name}>"

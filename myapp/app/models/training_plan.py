from datetime import datetime
from myapp.app import db


class TrainingPlan(db.Model):
    __tablename__ = "training_plans"

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey("users.id"), nullable=False)

    plan_json = db.Column(db.Text, nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    def __repr__(self):
        return f"<TrainingPlan user_id={self.user_id} created_at={self.created_at}>"

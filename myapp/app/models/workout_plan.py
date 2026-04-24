from myapp.app.extensions import db
from sqlalchemy.dialects.postgresql import JSONB


class WorkoutPlan(db.Model):
    __tablename__ = "workout_plans"

    id = db.Column(db.Integer, primary_key=True)
    plan = db.Column(JSONB, nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey("users.id"), nullable=False)

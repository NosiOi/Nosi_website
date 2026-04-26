from datetime import datetime
from myapp.app import db


class FitnessAssessment(db.Model):
    __tablename__ = "fitness_assessments"

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey("users.id"), nullable=False)

    pushups = db.Column(db.Integer, nullable=False)
    squats = db.Column(db.Integer, nullable=False)
    plank_seconds = db.Column(db.Integer, nullable=False)

    si_push = db.Column(db.Float, nullable=False)
    si_squat = db.Column(db.Float, nullable=False)
    si_core = db.Column(db.Float, nullable=False)

    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    user = db.relationship("User", backref=db.backref("fitness_assessments", lazy=True))

    def __repr__(self) -> str:
        return f"<FitnessAssessment user_id={self.user_id} si_push={self.si_push:.2f}>"

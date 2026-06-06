from datetime import datetime
from myapp.app import db


class TrainingSession(db.Model):
    __tablename__ = "training_sessions"

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey("users.id"), nullable=False)

    started_at = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)
    finished_at = db.Column(db.DateTime)

    status = db.Column(db.String(20), default="active")  # active, finished, aborted

    fatigue_before = db.Column(db.Float)
    fatigue_after = db.Column(db.Float)

    rpe_avg = db.Column(db.Float)

    exercises = db.relationship("SessionExercise", backref="session", lazy=True)


class SessionExercise(db.Model):
    __tablename__ = "session_exercises"

    id = db.Column(db.Integer, primary_key=True)
    session_id = db.Column(db.Integer, db.ForeignKey("training_sessions.id"), nullable=False)

    exercise_id = db.Column(db.String(64), nullable=False)
    sets_planned = db.Column(db.Integer, nullable=False)
    sets_done = db.Column(db.Integer, default=0)

    reps_planned = db.Column(db.String(32))
    reps_done = db.Column(db.String(32))

    load_planned = db.Column(db.Float)
    load_done = db.Column(db.Float)

    rpe = db.Column(db.Float)

from myapp.app import db


class PerformanceState(db.Model):
    __tablename__ = "performance_state"

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey("users.id"), nullable=False)

    pushups = db.Column(db.Integer, default=0)
    squats = db.Column(db.Integer, default=0)
    situps = db.Column(db.Integer, default=0)

    created_at = db.Column(db.DateTime, server_default=db.func.now())

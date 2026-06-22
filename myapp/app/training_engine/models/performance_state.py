from myapp.app import db

class PerformanceState(db.Model):
    __tablename__ = "te_performance_state"

    id = db.Column(db.Integer, primary_key=True)

    pushups = db.Column(db.Integer, default=0)
    squats = db.Column(db.Integer, default=0)
    situps = db.Column(db.Integer, default=0)

    plank_sec = db.Column(db.Integer, default=0)

    weight = db.Column(db.Float, nullable=True)
    training_load = db.Column(db.Float, default=0.0)

    user = db.relationship("User", back_populates="performance_state", uselist=False)

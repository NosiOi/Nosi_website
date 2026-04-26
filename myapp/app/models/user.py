from myapp.app import db


class User(db.Model):
    __tablename__ = "users"

    id = db.Column(db.Integer, primary_key=True)

    username = db.Column(db.String(50), nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password = db.Column(db.String(200), nullable=False)

    age = db.Column(db.Integer, nullable=False)
    height = db.Column(db.Float, nullable=False)
    weight = db.Column(db.Float, nullable=False)
    gender = db.Column(db.String(10), nullable=False)

    activity = db.Column(db.Float, nullable=False)

    goal = db.Column(db.String(50), nullable=False)
    experience = db.Column(db.String(50), nullable=False)
    workouts_per_week = db.Column(db.Integer, nullable=False)

    training_plans = db.relationship("TrainingPlan", backref="user", lazy=True)

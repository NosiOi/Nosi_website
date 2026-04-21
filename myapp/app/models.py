from datetime import datetime
from myapp.app.extensions import db


class User(db.Model):
    __tablename__ = "users"

    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(120), unique=True, nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password = db.Column(db.String(255), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    workouts = db.relationship("Workout", backref="user", lazy=True)
    nutrition = db.relationship("Nutrition", backref="user", lazy=True)
    recovery = db.relationship("Recovery", backref="user", lazy=True)


class Workout(db.Model):
    __tablename__ = "workouts"

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey("users.id"), nullable=False)
    type = db.Column(db.String(100), nullable=False)
    duration = db.Column(db.Integer, nullable=False)  # хвилини
    calories = db.Column(db.Integer)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)


class Nutrition(db.Model):
    __tablename__ = "nutrition"

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey("users.id"), nullable=False)
    calories = db.Column(db.Integer, nullable=False)
    protein = db.Column(db.Float)
    carbs = db.Column(db.Float)
    fat = db.Column(db.Float)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)


class Recovery(db.Model):
    __tablename__ = "recovery"

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey("users.id"), nullable=False)
    sleep_hours = db.Column(db.Float)
    stress_level = db.Column(db.Integer)  # 1–10
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

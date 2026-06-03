from flask_login import UserMixin
from myapp.app import db


class User(db.Model, UserMixin):
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

    is_premium = db.Column(db.Boolean, default=False)

    workout_plan = db.relationship("WorkoutPlan", backref="user", cascade="all, delete-orphan", lazy=True)
    nutrition_plan = db.relationship("NutritionPlan", backref="user", cascade="all, delete-orphan", lazy=True)
    recovery_plan = db.relationship("RecoveryPlan", backref="user", cascade="all, delete-orphan", lazy=True)
    
    assessments = db.relationship(
    "FitnessAssessment",
    back_populates="user",
    cascade="all, delete-orphan"
    )
    equipment = db.relationship("UserEquipment", back_populates="user", cascade="all, delete-orphan", lazy=True)

    meals = db.relationship(
    "Meal",
    back_populates="user",
    cascade="all, delete-orphan",
    lazy=True
    )
    
    oauth_accounts = db.relationship(
    "OAuthAccount",
    back_populates="user",
    cascade="all, delete-orphan"
    )



    @property
    def is_active(self):
        return True


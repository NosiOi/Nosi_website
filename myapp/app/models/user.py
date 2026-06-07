from flask_login import UserMixin
from myapp.app import db


class User(db.Model, UserMixin):
    __tablename__ = "users"

    id = db.Column(db.Integer, primary_key=True)

    # Basic info
    username = db.Column(db.String(50), nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password = db.Column(db.String(200), nullable=False)

    # Physical data
    age = db.Column(db.Integer, nullable=False)
    height = db.Column(db.Float, nullable=False)
    weight = db.Column(db.Float, nullable=False)
    gender = db.Column(db.String(10), nullable=False)

    # Activity & goals
    activity = db.Column(db.Float, nullable=False)
    goal = db.Column(db.String(50), nullable=False)
    experience = db.Column(db.String(50), nullable=False)
    workouts_per_week = db.Column(db.Integer, nullable=False)

    # Premium
    is_premium = db.Column(db.Boolean, default=False)

    # RELATIONSHIPS (SAFE, NON-CONFLICTING)

    # Nutrition plan (1:1)
    nutrition_plan = db.relationship(
        "NutritionPlan",
        backref="user",
        uselist=False,
        cascade="all, delete-orphan"
    )

    # Recovery plan (1:1)
    recovery_plan = db.relationship(
        "RecoveryPlan",
        backref="user",
        uselist=False,
        cascade="all, delete-orphan"
    )

    # Equipment (1:N)
    equipment = db.relationship(
        "UserEquipment",
        back_populates="user",
        cascade="all, delete-orphan",
        lazy=True
    )

    # Meals (1:N)
    meals = db.relationship(
        "Meal",
        back_populates="user",
        cascade="all, delete-orphan",
        lazy=True
    )

    # OAuth accounts (1:N)
    oauth_accounts = db.relationship(
        "OAuthAccount",
        back_populates="user",
        cascade="all, delete-orphan",
        lazy=True
    )

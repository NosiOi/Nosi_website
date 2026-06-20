from datetime import datetime
from flask_login import UserMixin
from myapp.app import db
from werkzeug.security import generate_password_hash, check_password_hash


class User(db.Model, UserMixin):
    __tablename__ = "users"

    id = db.Column(db.Integer, primary_key=True)

    # Basic info
    username = db.Column(db.String(50), nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password = db.Column(db.String(200), nullable=False)

    # Premium
    is_premium = db.Column(db.Boolean, default=False)

    # Timestamps
    created_at = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)

    # Workout / nutrition / recovery plans (1:1)
    workout_plan = db.relationship(
        "WorkoutPlan",
        back_populates="user",
        uselist=False,
        cascade="all, delete-orphan"
    )

    nutrition_plan = db.relationship(
        "NutritionPlan",
        back_populates="user",
        uselist=False,
        cascade="all, delete-orphan"
    )

    recovery_plan = db.relationship(
        "RecoveryPlan",
        back_populates="user",
        uselist=False,
        cascade="all, delete-orphan"
    )

    # Equipment (1:N)
    user_equipment = db.relationship(
        "UserEquipment",
        back_populates="user",
        cascade="all, delete-orphan",
        lazy="dynamic",
        foreign_keys="UserEquipment.user_id"
    )

    # Meals (1:N)
    meals = db.relationship(
        "Meal",
        back_populates="user",
        cascade="all, delete-orphan",
        lazy="dynamic",
        foreign_keys="Meal.user_id"
    )

    # OAuth accounts (1:N)
    oauth_accounts = db.relationship(
        "OAuthAccount",
        back_populates="user",
        cascade="all, delete-orphan",
        lazy="dynamic",
        foreign_keys="OAuthAccount.user_id"
    )

    # Training engine relationships
    training_plans = db.relationship(
        "TrainingPlan",
        back_populates="owner",
        cascade="all, delete-orphan",
        lazy="dynamic",
        foreign_keys="TrainingPlan.user_id"
    )

    sessions = db.relationship(
        "Session",
        back_populates="owner",
        cascade="all, delete-orphan",
        lazy="dynamic",
        foreign_keys="Session.user_id"
    )

    preferences = db.relationship(
        "UserPreference",
        back_populates="user",
        cascade="all, delete-orphan",
        lazy="dynamic",
        foreign_keys="UserPreference.user_id"
    )

    def set_password(self, password):
        self.password = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password, password)

    def __repr__(self):
        return f"<User id={self.id} username={self.username}>"

from myapp.app.extensions import db


class User(db.Model):
    __tablename__ = "users"

    id = db.Column(db.Integer, primary_key=True)

    # Основні дані
    username = db.Column(db.String(50), nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password = db.Column(db.String(200), nullable=False)

    # Антропометрія — тепер правильні типи
    age = db.Column(db.Integer, nullable=False)
    height = db.Column(db.Float, nullable=False)  # см
    weight = db.Column(db.Float, nullable=False)  # кг
    gender = db.Column(db.String(10), nullable=False)

    # Рівень активності — тепер float (1.2, 1.375, 1.55...)
    activity = db.Column(db.Float, nullable=False)

    # Цілі та досвід
    goal = db.Column(db.String(50), nullable=False)
    experience = db.Column(db.String(50), nullable=False)
    workouts_per_week = db.Column(db.Integer, nullable=False)

    # Зв'язки з планами
    workout_plan = db.relationship("WorkoutPlan", backref="user", lazy=True)
    nutrition_plan = db.relationship("NutritionPlan", backref="user", lazy=True)
    recovery_plan = db.relationship("RecoveryPlan", backref="user", lazy=True)


class WorkoutPlan(db.Model):
    __tablename__ = "workout_plans"

    id = db.Column(db.Integer, primary_key=True)
    plan = db.Column(db.Text, nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey("users.id"), nullable=False)


class NutritionPlan(db.Model):
    __tablename__ = "nutrition_plans"

    id = db.Column(db.Integer, primary_key=True)
    calories = db.Column(db.Integer, nullable=False)
    protein = db.Column(db.Integer, nullable=False)
    fats = db.Column(db.Integer, nullable=False)
    carbs = db.Column(db.Integer, nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey("users.id"), nullable=False)


class RecoveryPlan(db.Model):
    __tablename__ = "recovery_plans"

    id = db.Column(db.Integer, primary_key=True)
    plan = db.Column(db.Text, nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey("users.id"), nullable=False)

from myapp.app import db
from datetime import date


class NutritionPlan(db.Model):
    __tablename__ = "nutrition_plans"

    id = db.Column(db.Integer, primary_key=True)
    calories = db.Column(db.Integer, nullable=False)
    protein = db.Column(db.Integer, nullable=False)
    fats = db.Column(db.Integer, nullable=False)
    carbs = db.Column(db.Integer, nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey("users.id"), nullable=False)
    date = db.Column(db.Date, nullable=False, default=date.today)

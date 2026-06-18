from myapp.app import db


class MealItem(db.Model):
    __tablename__ = "meal_items"

    id = db.Column(db.Integer, primary_key=True)
    meal_id = db.Column(db.Integer, db.ForeignKey("meals.id"), nullable=False)

    name = db.Column(db.String(120), nullable=False)
    weight = db.Column(db.Float, nullable=True)

    calories = db.Column(db.Integer, nullable=False, default=0)
    protein = db.Column(db.Integer, nullable=False, default=0)
    fat = db.Column(db.Integer, nullable=False, default=0)
    carbs = db.Column(db.Integer, nullable=False, default=0)

    fiber = db.Column(db.Integer, default=0)
    category_label = db.Column(db.String(50), nullable=True)

    category_id = db.Column(db.Integer, db.ForeignKey("categories.id"), nullable=True)

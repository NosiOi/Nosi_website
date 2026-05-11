from myapp.app import db


class Meal(db.Model):
    __tablename__ = "meals"

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey("users.id"), nullable=False)

    date = db.Column(db.Date, nullable=False)
    time = db.Column(db.Time, nullable=True)
    is_daily_summary = db.Column(db.Boolean, nullable=False, default=False)

    total_calories = db.Column(db.Integer, nullable=False, default=0)
    total_protein = db.Column(db.Integer, nullable=False, default=0)
    total_fat = db.Column(db.Integer, nullable=False, default=0)
    total_carbs = db.Column(db.Integer, nullable=False, default=0)

    items = db.relationship("MealItem", backref="meal", lazy=True, cascade="all, delete-orphan")

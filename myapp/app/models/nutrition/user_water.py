from myapp.app import db
from datetime import date

class UserWater(db.Model):
    __tablename__ = "user_water"

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey("users.id"), nullable=False)
    date = db.Column(db.Date, default=date.today, nullable=False)
    amount = db.Column(db.Float, default=0)

from myapp.app import db


class UserGoals(db.Model):
    __tablename__ = "user_goals"

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey("users.id"), nullable=False, unique=True)

    calories_goal = db.Column(db.Integer, nullable=False, default=0)
    protein_goal = db.Column(db.Integer, nullable=False, default=0)
    fat_goal = db.Column(db.Integer, nullable=False, default=0)
    carb_goal = db.Column(db.Integer, nullable=False, default=0)

from myapp.app import db


class UserWeightHistory(db.Model):
    __tablename__ = "user_weight_history"

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey("users.id"), nullable=False)

    weight = db.Column(db.Float, nullable=False)
    date = db.Column(db.Date, nullable=False)

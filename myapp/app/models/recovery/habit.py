from myapp.app import db


class RecoveryHabit(db.Model):
    __tablename__ = "recovery_habits"

    id = db.Column(db.Integer, primary_key=True)

    name = db.Column(db.String(128), nullable=False)
    icon = db.Column(db.String(64), nullable=True)
    category = db.Column(db.String(64), nullable=True)

    premium_only = db.Column(db.Boolean, default=False, nullable=False)
    sort_order = db.Column(db.Integer, default=0, nullable=False)
    is_active = db.Column(db.Boolean, default=True, nullable=False)

    user_habits = db.relationship("UserRecoveryHabit", back_populates="habit")

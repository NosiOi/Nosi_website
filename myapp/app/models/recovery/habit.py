from myapp.app import db


class RecoveryHabit(db.Model):
    __tablename__ = "recovery_habits"

    id = db.Column(db.Integer, primary_key=True)

    name = db.Column(db.String(128), nullable=False, unique=True)
    icon = db.Column(db.String(64))
    category = db.Column(db.String(64))
    description = db.Column(db.String(256))

    users = db.relationship(
        "UserRecoveryHabit",
        back_populates="habit",
        cascade="all, delete-orphan",
        lazy="dynamic",
    )

    premium_only = db.Column(db.Boolean, nullable=False, default=False)
    sort_order = db.Column(db.Integer, nullable=False, default=0)
    is_active = db.Column(db.Boolean, nullable=False, default=True)

    user_habits = db.relationship(
        "UserRecoveryHabit", back_populates="habit", cascade="all, delete-orphan"
    )

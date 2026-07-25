from myapp.app import db


class RecoveryHabit(db.Model):
    __tablename__ = "recovery_habits"

    id = db.Column(db.Integer, primary_key=True)

    slug = db.Column(db.String(64), nullable=False, unique=True)
    name = db.Column(db.String(128), nullable=False, unique=True)
    description = db.Column(db.String(256))

    category = db.Column(db.String(64))
    icon = db.Column(db.String(64))

    points = db.Column(db.Integer, nullable=False, default=0)
    daily_limit = db.Column(db.Integer, nullable=False, default=1)
    estimated_minutes = db.Column(db.Integer, nullable=False, default=0)

    recommended_when = db.Column(db.JSON, nullable=False, default=list)

    premium_only = db.Column(db.Boolean, nullable=False, default=False)
    sort_order = db.Column(db.Integer, nullable=False, default=0)
    is_active = db.Column(db.Boolean, nullable=False, default=True)

    users = db.relationship(
        "UserRecoveryHabit",
        back_populates="habit",
        cascade="all, delete-orphan",
        lazy="dynamic",
    )

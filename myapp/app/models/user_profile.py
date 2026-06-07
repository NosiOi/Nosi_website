from myapp.app import db

class UserProfile(db.Model):
    __tablename__ = "user_profiles"

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey("users.id"), nullable=False, unique=True)

    training_location = db.Column(db.String(32), nullable=False)  # home, gym, outdoor
    wants_nutrition = db.Column(db.Boolean, default=False)
    wants_recovery = db.Column(db.Boolean, default=False)

    onboarding_completed = db.Column(db.Boolean, default=False)

    user = db.relationship("User", backref=db.backref("profile", uselist=False))

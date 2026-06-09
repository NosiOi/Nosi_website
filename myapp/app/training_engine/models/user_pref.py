from datetime import datetime
from myapp.app import db


class UserPreference(db.Model):
    __tablename__ = "te_user_preferences"

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, nullable=False, index=True)
    key = db.Column(db.String(120), nullable=False, index=True)
    value = db.Column(db.Text, nullable=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)

    def to_dict(self):
        return {"id": self.id, "user_id": self.user_id, "key": self.key, "value": self.value}

    def __repr__(self):
        return f"<UserPreference user_id={self.user_id} key={self.key}>"

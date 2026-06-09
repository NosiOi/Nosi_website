from datetime import datetime
from myapp.app import db


class Session(db.Model):
    __tablename__ = "te_sessions"

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey("users.id"), nullable=False, index=True)

    plan_id = db.Column(db.Integer, nullable=True)
    title = db.Column(db.String(250), nullable=True)
    started_at = db.Column(db.DateTime, nullable=True)
    finished_at = db.Column(db.DateTime, nullable=True)
    data = db.Column(db.Text, nullable=True)  # JSON log of sets, weights, timestamps

    created_at = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)

    owner = db.relationship(
        "User",
        back_populates="sessions",
        foreign_keys=[user_id]
    )

    def to_dict(self):
        return {
            "id": self.id,
            "user_id": self.user_id,
            "plan_id": self.plan_id,
            "title": self.title,
            "started_at": self.started_at.isoformat() if self.started_at else None,
            "finished_at": self.finished_at.isoformat() if self.finished_at else None,
            "data": self.data
        }

    def __repr__(self):
        return f"<Session id={self.id} user_id={self.user_id}>"

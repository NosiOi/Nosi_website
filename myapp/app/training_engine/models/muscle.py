from datetime import datetime
from myapp.app import db


class Muscle(db.Model):
    __tablename__ = "te_muscles"

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(120), nullable=False, unique=True)
    slug = db.Column(db.String(120), nullable=False, unique=True)
    description = db.Column(db.Text, nullable=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)

    def to_dict(self):
        return {"id": self.id, "name": self.name, "slug": self.slug, "description": self.description}

    def __repr__(self):
        return f"<Muscle id={self.id} slug={self.slug}>"

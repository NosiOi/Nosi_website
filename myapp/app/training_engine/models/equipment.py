from datetime import datetime
from myapp.app import db


class TEEquipment(db.Model):
    __tablename__ = "te_equipment"

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(200), nullable=False, unique=True)
    tags = db.Column(db.Text, nullable=True)
    description = db.Column(db.Text, nullable=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)

    def to_dict(self):
        return {"id": self.id, "name": self.name, "tags": self.tags, "description": self.description}

    def __repr__(self):
        return f"<TEEquipment id={self.id} name={self.name}>"

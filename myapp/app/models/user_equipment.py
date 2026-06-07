from myapp.app import db

class UserEquipment(db.Model):
    __tablename__ = "user_equipment"

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey("users.id"), nullable=False)
    equipment_id = db.Column(db.Integer, db.ForeignKey("equipment.id"), nullable=False)

    # Relationships
    user = db.relationship("User", back_populates="equipment")
    equipment = db.relationship("Equipment")

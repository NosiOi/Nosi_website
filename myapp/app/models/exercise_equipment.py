from myapp.app import db


class ExerciseEquipment(db.Model):
    __tablename__ = "exercise_equipment"

    exercise_id = db.Column(db.Integer, db.ForeignKey("exercises.id"), primary_key=True)
    equipment_id = db.Column(
        db.Integer, db.ForeignKey("equipment.id"), primary_key=True
    )

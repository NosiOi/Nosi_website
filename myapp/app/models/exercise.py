from myapp.app import db
from .exercise_equipment import ExerciseEquipment


class Exercise(db.Model):
    __tablename__ = "exercises"

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)

    muscle_group = db.Column(
        db.String(50), nullable=False
    )  # push, pull, legs, core, full
    strength_type = db.Column(db.String(50), nullable=True)  # push, legs, core

    difficulty = db.Column(db.Float, nullable=False, default=0.3)
    min_strength_index = db.Column(db.Float, nullable=False, default=0.0)
    min_experience = db.Column(db.Float, nullable=False, default=0.0)

    equipment = db.relationship(
        "Equipment", secondary="exercise_equipment", back_populates="exercises"
    )

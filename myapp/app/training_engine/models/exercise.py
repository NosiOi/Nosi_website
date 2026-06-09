from datetime import datetime
from myapp.app import db

exercise_muscle = db.Table(
    "te_exercise_muscle",
    db.Column("exercise_id", db.Integer, db.ForeignKey("te_exercises.id"), primary_key=True),
    db.Column("muscle_id", db.Integer, db.ForeignKey("te_muscles.id"), primary_key=True),
    db.Column("is_primary", db.Boolean, default=False)
)

exercise_equipment = db.Table(
    "te_exercise_equipment",
    db.Column("exercise_id", db.Integer, db.ForeignKey("te_exercises.id"), primary_key=True),
    db.Column("equipment_id", db.Integer, db.ForeignKey("te_equipment.id"), primary_key=True)
)


class Exercise(db.Model):
    __tablename__ = "te_exercises"

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(250), nullable=False, unique=True)
    slug = db.Column(db.String(250), nullable=False, unique=True)
    description = db.Column(db.Text, nullable=True)
    difficulty = db.Column(db.Integer, default=1)  # 1..10
    location = db.Column(db.String(30), default="any")  # gym, home, any
    movement_pattern = db.Column(db.String(50), nullable=True)
    risk_level = db.Column(db.Integer, default=1)  # 1..5
    progression = db.Column(db.Text, nullable=True)  # JSON list of slugs/ids
    regression = db.Column(db.Text, nullable=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)

    muscles = db.relationship("Muscle", secondary=exercise_muscle, backref=db.backref("exercises", lazy="dynamic"))
    equipment = db.relationship("TEEquipment", secondary=exercise_equipment, backref=db.backref("exercises", lazy="dynamic"))

    def is_bodyweight(self):
        return any(e.name.lower() == "bodyweight" for e in self.equipment) or len(self.equipment) == 0

    def to_dict(self):
        return {
            "id": self.id,
            "name": self.name,
            "slug": self.slug,
            "description": self.description,
            "difficulty": self.difficulty,
            "location": self.location,
            "movement_pattern": self.movement_pattern,
            "risk_level": self.risk_level,
            "muscles": [m.slug for m in self.muscles],
            "equipment": [e.name for e in self.equipment],
            "progression": self.progression,
            "regression": self.regression
        }

    def __repr__(self):
        return f"<Exercise id={self.id} name={self.name}>"

from datetime import datetime
from myapp.app import db
import json

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

    id = db.Column(db.String(250), primary_key=True)
    name = db.Column(db.String(250), nullable=False, unique=True)
    slug = db.Column(db.String(250), nullable=True, unique=False)
    description = db.Column(db.Text, nullable=True)
    difficulty = db.Column(db.Integer, default=1)
    location = db.Column(db.String(30), default="any")
    movement_pattern = db.Column(db.String(50), nullable=True)
    risk_level = db.Column(db.Integer, default=1)
    progression = db.Column(db.Text, nullable=True)
    regression = db.Column(db.Text, nullable=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)

    muscles = db.relationship("Muscle", secondary=exercise_muscle, backref=db.backref("exercises", lazy="dynamic"))
    equipment = db.relationship("TEEquipment", secondary=exercise_equipment, backref=db.backref("exercises", lazy="dynamic"))

    def __init__(self, *args, **kwargs):
        """
        Accept legacy/test kwargs (muscles_primary, muscles_secondary, equipment, environment,
        progression_chain, regression_chain, movement_pattern, risk_level, difficulty, id, name, slug).
        Unknown kwargs are set as plain attributes for in-memory tests.
        """
        # Known mapped fields to pass to SQLAlchemy constructor
        mapped = {}
        for k in ("id", "name", "slug", "description", "difficulty", "location", "movement_pattern", "risk_level", "progression", "regression"):
            if k in kwargs:
                mapped[k] = kwargs.pop(k)

        # call base constructor to set mapped attributes
        super().__init__(**mapped)

        # handle legacy lists -> store as attributes (not necessarily DB columns)
        # progression_chain / regression_chain -> store as JSON text in progression/regression columns
        prog = kwargs.pop("progression_chain", kwargs.pop("progression", None))
        reg = kwargs.pop("regression_chain", kwargs.pop("regression", None))
        if prog is not None:
            try:
                self.progression = json.dumps(prog)
            except Exception:
                self.progression = str(prog)
        if reg is not None:
            try:
                self.regression = json.dumps(reg)
            except Exception:
                self.regression = str(reg)

        # environment/equipment/muscles_primary/muscles_secondary: keep as plain attributes for tests
        if "environment" in kwargs:
            self.environment = kwargs.pop("environment")
        if "equipment" in kwargs:
            self._legacy_equipment = kwargs.pop("equipment")
        if "muscles_primary" in kwargs:
            self._muscles_primary = kwargs.pop("muscles_primary")
        if "muscles_secondary" in kwargs:
            self._muscles_secondary = kwargs.pop("muscles_secondary")

        # set any remaining kwargs as attributes (for test compatibility)
        for k, v in kwargs.items():
            setattr(self, k, v)

    def is_bodyweight(self):
        try:
            return any(e.name.lower() == "bodyweight" for e in self.equipment) or getattr(self, "_legacy_equipment", None) == ["bodyweight"] or len(self.equipment) == 0
        except Exception:
            return False

    def to_dict(self):
        # safe serialization for API/tests
        muscles = []
        try:
            muscles = [{"id": m.id, "name": m.name, "slug": m.slug} for m in self.muscles]
        except Exception:
            muscles = getattr(self, "_muscles_primary", []) + getattr(self, "_muscles_secondary", [])
        equipment = []
        try:
            equipment = [{"id": e.id, "name": e.name} for e in self.equipment]
        except Exception:
            equipment = getattr(self, "_legacy_equipment", []) or []
        return {
            "id": self.id,
            "name": self.name,
            "slug": self.slug,
            "description": self.description,
            "difficulty": self.difficulty,
            "location": self.location,
            "movement_pattern": self.movement_pattern,
            "risk_level": self.risk_level,
            "muscles": muscles,
            "equipment": equipment,
            "progression": self.progression,
            "regression": self.regression
        }

    def __repr__(self):
        return f"<Exercise id={self.id} name={self.name}>"

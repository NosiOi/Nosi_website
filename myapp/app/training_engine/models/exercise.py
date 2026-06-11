from datetime import datetime
from myapp.app import db
import json

exercise_muscle = db.Table(
    "te_exercise_muscle",
    db.Column("exercise_id", db.String(250), db.ForeignKey("te_exercises.id"), primary_key=True),
    db.Column("muscle_id", db.Integer, db.ForeignKey("te_muscles.id"), primary_key=True),
    db.Column("is_primary", db.Boolean, default=False)
)

exercise_equipment = db.Table(
    "te_exercise_equipment",
    db.Column("exercise_id", db.String(250), db.ForeignKey("te_exercises.id"), primary_key=True),
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

    muscles = db.relationship(
        "Muscle",
        secondary=exercise_muscle,
        backref=db.backref("exercises", lazy="dynamic")
    )
    equipment = db.relationship(
        "TEEquipment",
        secondary=exercise_equipment,
        backref=db.backref("exercises", lazy="dynamic")
    )

    def __init__(self, *args, **kwargs):
        """
        Accept legacy/test kwargs (muscles_primary, muscles_secondary, equipment, environment,
        progression_chain, regression_chain, movement_pattern, risk_level, difficulty, id, name, slug).
        Unknown kwargs are set as plain attributes for in-memory tests.
        """
        # Known mapped fields to pass to SQLAlchemy constructor
        mapped = {}
        for k in (
            "id",
            "name",
            "slug",
            "description",
            "difficulty",
            "location",
            "movement_pattern",
            "risk_level",
            "progression",
            "regression",
        ):
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
            self._progression_chain = list(prog) if isinstance(prog, (list, tuple)) else []
        else:
            self._progression_chain = []

        if reg is not None:
            try:
                self.regression = json.dumps(reg)
            except Exception:
                self.regression = str(reg)
            self._regression_chain = list(reg) if isinstance(reg, (list, tuple)) else []
        else:
            self._regression_chain = []

        if "environment" in kwargs:
            self._environment = kwargs.pop("environment")
        else:
            self._environment = []

        if "equipment" in kwargs:
            self._legacy_equipment = kwargs.pop("equipment")
        else:
            self._legacy_equipment = []

        if "muscles_primary" in kwargs:
            self._muscles_primary = kwargs.pop("muscles_primary")
        else:
            self._muscles_primary = []

        if "muscles_secondary" in kwargs:
            self._muscles_secondary = kwargs.pop("muscles_secondary")
        else:
            self._muscles_secondary = []

        for k, v in kwargs.items():
            setattr(self, k, v)

    # --- compatibility properties for tests / loaders ---
    @property
    def muscles_primary(self):
        if getattr(self, "_muscles_primary", None):
            return list(self._muscles_primary)
        # derive from association if exercise_muscles relationship exists
        try:
            res = []
            for em in getattr(self, "exercise_muscles", []) or []:
                if getattr(em, "is_primary", False):
                    m = getattr(em, "muscle", None)
                    if m and getattr(m, "slug", None):
                        res.append(m.slug)
            if res:
                return res
        except Exception:
            pass
        return []

    @property
    def muscles_secondary(self):
        if getattr(self, "_muscles_secondary", None):
            return list(self._muscles_secondary)
        return []

    @property
    def progression_chain(self):
        # prefer in-memory list
        if getattr(self, "_progression_chain", None):
            return list(self._progression_chain)
        try:
            if self.progression:
                return json.loads(self.progression)
        except Exception:
            pass
        return []

    @property
    def regression_chain(self):
        if getattr(self, "_regression_chain", None):
            return list(self._regression_chain)
        try:
            if self.regression:
                return json.loads(self.regression)
        except Exception:
            pass
        return []

    @property
    def environment(self):
        # environment may be stored as list or single value
        env = getattr(self, "_environment", None)
        if env is None:
            return []
        return env if isinstance(env, (list, tuple)) else [env]

    # --- utility methods ---
    def is_bodyweight(self):
        try:
            if getattr(self, "_legacy_equipment", None):
                if isinstance(self._legacy_equipment, (list, tuple)):
                    return "bodyweight" in [e.lower() for e in self._legacy_equipment if isinstance(e, str)]
                return str(self._legacy_equipment).lower() == "bodyweight"
            return any(e.name.lower() == "bodyweight" for e in self.equipment) or len(self.equipment) == 0
        except Exception:
            return False

    def to_dict(self):
        # safe serialization for API/tests
        muscles = []
        try:
            muscles = [{"id": m.id, "name": m.name, "slug": m.slug} for m in self.muscles]
        except Exception:
            # fallback to legacy lists
            muscles = [{"slug": s} for s in (getattr(self, "_muscles_primary", []) + getattr(self, "_muscles_secondary", []))]
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

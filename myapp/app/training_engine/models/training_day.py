from dataclasses import dataclass, field
from typing import Any, Dict, List, Optional

@dataclass
class TrainingDay:
    day_name: Optional[str] = None
    name: Optional[str] = None
    environment: Optional[List[str]] = None
    exercises: List[Dict[str, Any]] = field(default_factory=list)

    def add_exercise(self, exercise=None, sets=3, reps="8-12", **kwargs):
        entry = {"exercise": exercise, "sets": sets, "reps": reps}
        entry.update(kwargs)
        self.exercises.append(entry)

    def total_volume(self):
        """
        Minimal helper used by tests: sum of sets * reps (if reps numeric).
        If reps is range/string, ignore or treat as 0.
        """
        total = 0
        for e in self.exercises:
            sets = e.get("sets", 0) or 0
            reps = e.get("reps", 0) or 0
            try:
                reps_int = int(str(reps).split("-")[0])
            except Exception:
                reps_int = 0
            try:
                total += int(sets) * int(reps_int)
            except Exception:
                pass
        return total

    # dictionary-like access used by PlanValidator in tests
    def get(self, key, default=None):
        if key == "exercises":
            return self.exercises
        if key == "environment":
            return self.environment
        return getattr(self, key, default)

    @classmethod
    def from_dict(cls, data: Dict[str, Any]):
        dn = data.get("day_name") or data.get("name")
        env = data.get("environment")
        exercises = data.get("exercises", []) or []
        return cls(day_name=dn, name=dn, environment=env, exercises=list(exercises))

    def to_dict(self):
        return {"day_name": self.day_name or self.name, "environment": self.environment, "exercises": list(self.exercises)}

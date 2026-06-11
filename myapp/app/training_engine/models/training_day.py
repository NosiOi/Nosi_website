from dataclasses import dataclass, field
from typing import Any, Dict, List, Optional

@dataclass
class TrainingDay:
    day_name: Optional[str] = None
    name: Optional[str] = None
    environment: Optional[List[str]] = None
    exercises: List[Dict[str, Any]] = field(default_factory=list)

    def add_exercise(self, exercise=None, sets=3, reps="8-12", **kwargs):
        """
        Tests call day.add_exercise(exercise=ex, sets=3, reps="10-12")
        Accept both positional and keyword args and append a normalized dict.
        """
        entry = {
            "exercise": exercise,
            "sets": sets,
            "reps": reps
        }
        # include any extra metadata
        for k, v in kwargs.items():
            entry[k] = v
        self.exercises.append(entry)

    @classmethod
    def from_dict(cls, data):
        dn = data.get("day_name") or data.get("name")
        env = data.get("environment")
        exercises = data.get("exercises", []) or []
        return cls(day_name=dn, name=dn, environment=env, exercises=list(exercises))

    def to_dict(self):
        return {"day_name": self.day_name or self.name, "environment": self.environment, "exercises": list(self.exercises)}

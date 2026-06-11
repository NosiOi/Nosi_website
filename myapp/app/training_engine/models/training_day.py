from dataclasses import dataclass, field
from typing import Any, Dict, List, Optional

@dataclass
class TrainingDay:
    day_name: Optional[str] = None
    name: Optional[str] = None
    environment: Optional[str] = None
    exercises: List[Dict[str, Any]] = field(default_factory=list)

    def add_exercise(self, ex):
        self.exercises.append(ex)

    @classmethod
    def from_dict(cls, data: Dict[str, Any]):
        dn = data.get("day_name") or data.get("name")
        env = data.get("environment")
        exercises = data.get("exercises", []) or []
        return cls(day_name=dn, name=dn, environment=env, exercises=list(exercises))

    def to_dict(self):
        return {"day_name": self.day_name or self.name, "environment": self.environment, "exercises": list(self.exercises)}

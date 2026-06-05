from dataclasses import dataclass, field
from typing import List, Dict
from .exercise import Exercise


@dataclass
class TrainingDay:
    """
    Represents a single training day inside a training plan.
    Contains:
    - list of exercises
    - metadata (goal, focus, environment)
    - adaptive load modifiers
    """

    day_name: str
    exercises: List[Dict] = field(default_factory=list)
    focus: str = "general"
    environment: str = "gym"

    def add_exercise(self, exercise: Exercise, sets: int, reps: str):
        self.exercises.append({
            "exercise": exercise,
            "sets": sets,
            "reps": reps,
        })

    def total_volume(self) -> int:
        """Rough volume estimation."""
        return sum(e["sets"] for e in self.exercises)

    # TODO: add RPE tracking
    # TODO: add fatigue impact calculation

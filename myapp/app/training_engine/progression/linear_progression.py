from dataclasses import dataclass
from typing import Dict


@dataclass
class LinearProgression:
    increment_percent: float = 0.05
    rep_increment: int = 2

    def next_load(self, current_load: float, completed: bool) -> float:
        if completed:
            return round(current_load * (1 + self.increment_percent), 2)
        return current_load

    def next_reps(self, current_reps: int, completed: bool) -> int:
        if completed:
            return current_reps + self.rep_increment
        return current_reps

    def apply(self, exercise_data: Dict, completed: bool) -> Dict:
        return {
            "load": self.next_load(exercise_data["load"], completed),
            "reps": self.next_reps(exercise_data["reps"], completed),
            "sets": exercise_data["sets"]
        }

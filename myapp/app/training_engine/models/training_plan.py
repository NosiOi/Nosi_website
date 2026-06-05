from dataclasses import dataclass, field
from typing import Dict, List
from .training_day import TrainingDay


@dataclass
class TrainingPlan:
    """
    High-level training plan model.
    Contains:
    - multiple training days
    - metadata about user and goal
    - periodization model reference
    """

    days: Dict[str, TrainingDay] = field(default_factory=dict)
    goal: str = "maintain"
    experience: str = "beginner"
    workouts_per_week: int = 3
    periodization: str = "linear"

    def add_day(self, name: str, day: TrainingDay):
        self.days[name] = day

    def get_day(self, name: str) -> TrainingDay:
        return self.days[name]

    def summary(self) -> Dict:
        return {
            "days": list(self.days.keys()),
            "goal": self.goal,
            "experience": self.experience,
            "workouts_per_week": self.workouts_per_week,
            "periodization": self.periodization,
        }

    # TODO: add deload week generator
    # TODO: add adaptive progression integration

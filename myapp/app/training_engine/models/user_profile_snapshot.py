from dataclasses import dataclass
from typing import List


@dataclass
class UserProfileSnapshot:
    """
    Immutable snapshot of user data at the moment of plan generation.
    Prevents inconsistencies when user updates profile later.
    """

    age: int
    sex: str
    weight: float
    height: float
    activity: float
    goal: str
    experience: str
    workouts_per_week: int
    environment: str
    weak_points: List[str]
    strong_points: List[str]

    # TODO: add body fat estimation
    # TODO: add metabolic age

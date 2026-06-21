from dataclasses import dataclass
from typing import List


@dataclass
class UserProfileSnapshot:
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
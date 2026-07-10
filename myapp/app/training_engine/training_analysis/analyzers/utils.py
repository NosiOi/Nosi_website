from typing import List
from myapp.app.training_engine.models.exercise import Exercise

MOVEMENT_PATTERNS = (
    "push",
    "pull",
    "hinge",
    "squat",
    "core",
    "carry",
    "rotation",
)


def pattern_key(p: str) -> str:
    p = (p or "").lower()
    for pattern in MOVEMENT_PATTERNS:
        if pattern in p:
            return pattern
    return "other"


def primary_muscles(ex: Exercise) -> List[str]:
    return [m.lower() for m in (ex.muscles_primary or [])]


def movement_pattern(ex: Exercise) -> str:
    return pattern_key(ex.movement_pattern)

from dataclasses import dataclass, field
from typing import List, Optional


@dataclass
class Exercise:
    """
    Core exercise model used across the Training Engine.
    This model describes:
    - primary and secondary muscle groups
    - difficulty level (1–10)
    - equipment requirements
    - movement pattern classification
    - risk level (1–5)
    - progression and regression chains
    """

    id: str
    name: str
    muscles_primary: List[str]
    muscles_secondary: List[str] = field(default_factory=list)
    difficulty: int = 1
    equipment: List[str] = field(default_factory=list)
    environment: List[str] = field(default_factory=list)
    movement_pattern: Optional[str] = None  # push, pull, hinge, squat, carry, rotation
    risk_level: int = 1
    progression_chain: List[str] = field(default_factory=list)
    regression_chain: List[str] = field(default_factory=list)

    def is_bodyweight(self) -> bool:
        return "bodyweight" in self.equipment or not self.equipment

    def is_safe_for_beginners(self) -> bool:
        return self.difficulty <= 3 and self.risk_level <= 2

    # TODO: add biomechanical metadata
    # TODO: add energy system classification (ATP-PC, glycolytic, oxidative)

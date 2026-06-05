from dataclasses import dataclass


@dataclass
class FatigueState:
    """
    Represents user's fatigue level.
    Used for:
    - adaptive load
    - deload logic
    - recovery recommendations
    """

    sleep_hours: float = 8.0
    stress_level: int = 1  # 1–5
    soreness_level: int = 1  # 1–5

    def fatigue_score(self) -> float:
        """Simple placeholder formula."""
        return (self.stress_level + self.soreness_level) - (self.sleep_hours / 2)

    # TODO: integrate with analytics.fatigue_model

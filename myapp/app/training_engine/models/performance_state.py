from dataclasses import dataclass


@dataclass
class PerformanceState:
    """
    Snapshot of user's physical performance.
    Includes:
    - strength metrics
    - endurance metrics
    - mobility metrics
    """

    pushups_max: int = 0
    squats_max: int = 0
    situps_max: int = 0
    plank_time_sec: int = 0

    def strength_index(self) -> float:
        """
        Basic strength index (placeholder).
        Will be replaced by analytics/strength_index.py.
        """
        return (self.pushups_max + self.squats_max + self.situps_max) / 3

    # TODO: integrate with analytics.strength_index
    # TODO: add VO2max estimation

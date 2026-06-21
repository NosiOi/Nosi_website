from dataclasses import dataclass


@dataclass
class Autoregulation:
    fatigue_threshold: float = 6.0
    reduction_percent: float = 0.15

    def adjust_load(self, load: float, fatigue_score: float) -> float:
        if fatigue_score > self.fatigue_threshold:
            return round(load * (1 - self.reduction_percent), 2)
        return load

    def adjust_reps(self, reps: int, fatigue_score: float) -> int:
        if fatigue_score > self.fatigue_threshold:
            return max(1, reps - 2)
        return reps

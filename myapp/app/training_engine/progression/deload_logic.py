from dataclasses import dataclass


@dataclass
class DeloadLogic:
    """
    Determines when a deload week is needed.

    Triggers:
    - high fatigue score
    - multiple high-RPE sessions
    - poor recovery
    """

    fatigue_trigger: float = 8.0
    rpe_trigger: int = 3  # 3 sessions with RPE >= 9
    reduction_percent: float = 0.30  # -30%

    def needs_deload(self, fatigue_score: float, high_rpe_sessions: int) -> bool:
        return fatigue_score > self.fatigue_trigger or high_rpe_sessions >= self.rpe_trigger

    def apply_deload(self, load: float, reps: int, sets: int) -> dict:
        return {
            "load": round(load * (1 - self.reduction_percent), 2),
            "reps": max(1, int(reps * 0.7)),
            "sets": max(1, int(sets * 0.7))
        }

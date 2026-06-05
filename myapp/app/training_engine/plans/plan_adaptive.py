from typing import Dict, List
from ..progression.autoregulation import Autoregulation
from ..progression.rpe_logic import RPELogic
from ..progression.deload_logic import DeloadLogic


class PlanAdaptive:

    # Applies adaptive logic to training plan: fatigue adjustments, RPE adjustments, deload logic

    def __init__(self):
        self.auto = Autoregulation()
        self.rpe = RPELogic()
        self.deload = DeloadLogic()

    def apply_fatigue(self, exercise_data: Dict, fatigue_score: float) -> Dict:
        exercise_data["load"] = self.auto.adjust_load(exercise_data["load"], fatigue_score)
        exercise_data["reps"] = self.auto.adjust_reps(exercise_data["reps"], fatigue_score)
        return exercise_data

    def apply_rpe(self, exercise_data: Dict, rpe: float) -> Dict:
        exercise_data["load"] = self.rpe.adjust_load(exercise_data["load"], rpe)
        exercise_data["reps"] = self.rpe.adjust_reps(exercise_data["reps"], rpe)
        return exercise_data

    def apply_deload_if_needed(self, exercise_data: Dict, fatigue_score: float, high_rpe_sessions: int) -> Dict:
        if self.deload.needs_deload(fatigue_score, high_rpe_sessions):
            return self.deload.apply_deload(
                exercise_data["load"],
                exercise_data["reps"],
                exercise_data["sets"]
            )
        return exercise_data

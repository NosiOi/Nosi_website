from dataclasses import dataclass


@dataclass
class RPELogic:
    def adjust_load(self, load: float, rpe: float) -> float:
        if rpe <= 6:
            return round(load * 1.05, 2)
        if rpe == 7:
            return round(load * 1.02, 2)
        if rpe == 8:
            return load
        if rpe == 9:
            return round(load * 0.97, 2)
        if rpe >= 10:
            return round(load * 0.90, 2)
        return load

    def adjust_reps(self, reps: int, rpe: float) -> int:
        if rpe <= 6:
            return reps + 2
        if rpe == 7:
            return reps + 1
        if rpe == 8:
            return reps
        if rpe == 9:
            return max(1, reps - 1)
        if rpe >= 10:
            return max(1, reps - 2)
        return reps

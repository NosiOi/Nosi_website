from typing import Dict, Any

class PlanValidator:
    @staticmethod
    def validate(days: Dict[str, Any]) -> bool:
        return PlanValidator.validate_plan(days)

    @staticmethod
    def validate_plan(days: Dict[str, Any]) -> bool:
        if not isinstance(days, dict):
            raise ValueError("Days must be a dict")
        if not days:
            raise ValueError("Plan must contain at least one day")
        for k, d in days.items():
            # support TrainingDay objects and dicts
            if hasattr(d, "get"):
                exercises = d.get("exercises", [])
            else:
                # dataclass TrainingDay: access attribute
                exercises = getattr(d, "exercises", [])
            if not isinstance(exercises, list):
                raise ValueError("Day exercises must be a list")
            if len(exercises) == 0:
                raise ValueError(f"Day {k} has no exercises")
        return True

from typing import Dict, Any

class PlanValidator:
    @staticmethod
    def validate_plan(days: Dict[str, Any]) -> bool:
        if not isinstance(days, dict):
            raise ValueError("Days must be a dict")
        if not days:
            raise ValueError("Plan must contain at least one day")
        for k, d in days.items():
            exercises = d.get("exercises", [])
            if not isinstance(exercises, list):
                raise ValueError("Day exercises must be a list")
        return True

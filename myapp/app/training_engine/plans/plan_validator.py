from typing import Dict, Any


class PlanValidator:
    @staticmethod
    def validate(days: Dict[str, Any]) -> bool:
        if not isinstance(days, dict):
            raise ValueError("Days must be a dict")
        if not days:
            raise ValueError("Plan must contain at least one day")
        for key, day in days.items():
            exercises = day.get("exercises", []) if hasattr(day, "get") else getattr(day, "exercises", [])
            if not isinstance(exercises, list):
                raise ValueError("Day exercises must be a list")
            if not exercises:
                raise ValueError(f"Day {key} has no exercises")
        return True

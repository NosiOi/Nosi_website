from typing import Dict


class PlanValidator:
    
    # Validates training plan structure.

    @staticmethod
    def validate(plan: Dict) -> bool:
        if not plan:
            return False

        for day, exercises in plan.items():
            if not isinstance(exercises, list):
                return False
            if len(exercises) == 0:
                return False

        return True

from ..models.exercise import Exercise


class ExerciseValidator:
    
    # Ensures exercise objects are valid and safe to use.

    @staticmethod
    def validate(ex: Exercise):
        if not ex.id or not isinstance(ex.id, str):
            raise ValueError("Exercise must have a valid ID")

        if not ex.name:
            raise ValueError("Exercise must have a name")

        if not ex.muscles_primary:
            raise ValueError("Exercise must have at least one primary muscle")

        if ex.difficulty < 1 or ex.difficulty > 10:
            raise ValueError("Difficulty must be between 1 and 10")

        if ex.risk_level < 1 or ex.risk_level > 5:
            raise ValueError("Risk level must be between 1 and 5")

        if not isinstance(ex.environment, list):
            raise ValueError("Environment must be a list")

        return True

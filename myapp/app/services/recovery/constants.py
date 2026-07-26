from enum import StrEnum


class RecoveryTrigger(StrEnum):
    LOW_RECOVERY = "low_recovery"
    AFTER_TRAINING = "after_training"
    LOW_ENERGY = "low_energy"
    SLEEP_DEFICIT = "sleep_deficit"
    STRESS = "stress"


class HabitCategory(StrEnum):
    HYDRATION = "hydration"
    SLEEP = "sleep"
    ACTIVITY = "activity"
    RECOVERY = "recovery"
    LIFESTYLE = "lifestyle"
    NUTRITION = "nutrition"


SLEEP_EXCELLENT = 480
SLEEP_GOOD = 420
SLEEP_OK = 360

SLEEP_WEIGHT = 0.45
TRAINING_WEIGHT = 0.25
HABIT_WEIGHT = 0.20
ENERGY_WEIGHT = 0.10

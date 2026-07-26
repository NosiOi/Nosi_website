from enum import StrEnum


class RecoveryTrigger(StrEnum):
    LOW_RECOVERY = "low_recovery"
    AFTER_TRAINING = "after_training"
    LOW_ENERGY = "low_energy"
    SLEEP_DEFICIT = "sleep_deficit"


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
HABIT_WEIGHT = 0.30

# Training load thresholds (internal load index)
TRAINING_LOAD_LOW = 40
TRAINING_LOAD_MEDIUM = 80
TRAINING_LOAD_HIGH = 120
TRAINING_LOAD_VERY_HIGH = 160
TRAINING_LOAD_EXTREME = 200

# Sleep debt configuration
SLEEP_DEBT_DAYS = 5
SLEEP_DEBT_DIVISOR = 20
SLEEP_DEFICIT_DIVISOR = 15

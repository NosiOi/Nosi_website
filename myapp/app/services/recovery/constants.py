from enum import StrEnum


class RecoveryTrigger(StrEnum):
    LOW_RECOVERY = "low_recovery"
    AFTER_HEAVY_TRAINING = "after_heavy_training"
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


# Base sleep targets (minutes) by age group
SLEEP_BASE_TEEN_MINUTES = 540  # 9h
SLEEP_BASE_ADULT_MINUTES = 480  # 8h
SLEEP_BASE_SENIOR_MINUTES = 450  # 7.5h

# Training load thresholds (internal load index)
TRAINING_LOAD_LOW = 40
TRAINING_LOAD_MEDIUM = 80
TRAINING_LOAD_HIGH = 120
TRAINING_LOAD_OPTIMAL = 160
TRAINING_LOAD_HEAVY = 140
TRAINING_LOAD_VERY_HEAVY = 180

# Sleep debt configuration
SLEEP_DEBT_DAYS = 5
SLEEP_DEBT_PENALTY_DIVISOR = 20  # minutes → points

# Recovery weights
SLEEP_WEIGHT = 0.45
TRAINING_WEIGHT = 0.25
HABIT_WEIGHT = 0.20
ENERGY_WEIGHT = 0.10

# Energy weights (normalized to 1.0)
ENERGY_SLEEP_WEIGHT = 0.75
ENERGY_HABIT_WEIGHT = 0.25

# Penalties
HEAVY_LOAD_RECOVERY_PENALTY = 10
VERY_HEAVY_LOAD_RECOVERY_PENALTY = 20

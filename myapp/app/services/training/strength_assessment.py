from dataclasses import dataclass

# Поки без віку/статі, беремо усереднені нормативи
PUSHUPS_NORM = 35  # середній рівень для 16–30 років
SQUATS_NORM = 60  # присідання з вагою тіла
PLANK_NORM = 90  # секунди


@dataclass
class StrengthIndex:
    si_push: float
    si_squat: float
    si_core: float


def _safe_div(x: int, norm: int) -> float:
    if norm <= 0:
        return 0.0
    if x <= 0:
        return 0.0
    return x / norm


def calculate_strength_index(
    pushups: int, squats: int, plank_seconds: int
) -> StrengthIndex:
    """
    Обчислює коефіцієнти сили (SI) для трьох зон:
    - push (груди/трицепс)
    - squat (ноги)
    - core (кор)
    """

    si_push = _safe_div(pushups, PUSHUPS_NORM)
    si_squat = _safe_div(squats, SQUATS_NORM)
    si_core = _safe_div(plank_seconds, PLANK_NORM)

    # легкий clamp, щоб не вилітати в космос
    si_push = max(0.05, min(si_push, 2.0))
    si_squat = max(0.05, min(si_squat, 2.0))
    si_core = max(0.05, min(si_core, 2.0))

    return StrengthIndex(
        si_push=si_push,
        si_squat=si_squat,
        si_core=si_core,
    )

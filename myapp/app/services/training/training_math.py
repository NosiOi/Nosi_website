def calc_sets(base_sets: int, strength_index: float) -> int:
    """
    Масштабуємо кількість підходів:
    слабший → ближче до base_sets
    сильніший → більше підходів
    """
    raw = base_sets * (0.8 + strength_index * 0.4)
    return max(1, round(raw))


def calc_reps(base_reps: int, strength_index: float) -> int:
    """
    Масштабуємо повторення:
    слабший → ближче до base_reps
    сильніший → більше повторень
    """
    raw = base_reps * (0.7 + strength_index * 0.5)
    return max(1, round(raw))


def calc_rest(base_rest: int, strength_index: float) -> int:
    """
    Масштабуємо відпочинок:
    слабший → більше відпочинку
    сильніший → менше
    base_rest у секундах
    """
    raw = base_rest * (1.2 - strength_index * 0.3)
    return max(30, round(raw))

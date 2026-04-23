def calculate_water(weight, activity):
    # Наприклад:
    base = weight * 0.03  # 30 мл на кг
    extra = (activity - 1.2) * 0.5  # бонус за активність
    return round(base + extra, 2)

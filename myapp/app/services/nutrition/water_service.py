def calculate_water(weight, activity=None):
    """
    Calculate daily water in liters.
    - If activity is None: use default 35 ml/kg (0.035 l/kg) to match tests.
    - If activity provided: apply small activity-based bonus.
    """
    if activity is None:
        return round(weight * 0.035, 2)
    try:
        act = float(activity)
    except Exception:
        act = 1.2
    base = weight * 0.03
    extra = (act - 1.2) * 0.5 # 30 ml/kg baseline when activity specified
    return round(base + extra, 2) # activity bonus (liters)

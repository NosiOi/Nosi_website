def calculate_bmr(weight, height, age, gender):
    if gender == "male":
        return 10 * weight + 6.25 * height - 5 * age + 5
    return 10 * weight + 6.25 * height - 5 * age - 161


def calculate_tdee(bmr, activity):
    return float(bmr) * float(activity)


def calculate_calories_goal(tdee, goal):
    if goal in ("maintain", "maintenance"):
        return tdee
    if goal in ("lose", "fat_loss", "cut"):
        return tdee * 0.85
    if goal in ("gain", "muscle_gain", "bulk"):
        return tdee * 1.12
    raise ValueError("Unknown goal")

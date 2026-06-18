def ml_per_kg_by_age(age):
    # This function returns how many ml of water per kg a person needs.

    if age is None:
        return 35

    if age <= 12:
        return 45

    if 13 <= age <= 17:
        return 45 - (age - 12) * (7 / 5)

    if 18 <= age <= 25:
        return 38 - (age - 17) * (2 / 8)

    if 26 <= age <= 40:
        return 36 - (age - 25) * (1 / 15)

    if 41 <= age <= 60:
        return 35 - (age - 40) * (2 / 20)

    if age >= 61:
        return max(30, 33 - (age - 60) * (3 / 40))

    return 35


def calculate_water(weight, height, age, gender, activity, goal):
    if not weight:
        return 0.0

    ml_per_kg = ml_per_kg_by_age(age)
    water = weight * ml_per_kg / 1000

    if gender == "male":
        water *= 1.03  # smaller correction

    if activity:
        try:
            act = float(activity)
        except:
            act = 1.2
        act = max(1.0, min(act, 2.0))
        water *= (1 + (act - 1.2) * 0.07)  # smaller activity impact

    if goal in ("lose", "fat_loss", "weight_loss"):
        water *= 1.05  # reduced from 10%
    elif goal in ("gain", "muscle_gain", "mass_gain"):
        water *= 1.02  # reduced from 5%

    water = max(1.5, min(water, 3.5))

    return round(water, 2)

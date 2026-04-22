def calculate_bmr(weight, height, age, gender):
    if gender == "male":
        return 10 * weight + 6.25 * height - 5 * age + 5
    return 10 * weight + 6.25 * height - 5 * age - 161


def calculate_tdee(bmr, activity):
    return bmr * activity


def calculate_calories_goal(tdee, goal):
    if goal == "maintain":
        return tdee
    if goal == "lose":
        return tdee * 0.85
    if goal == "gain":
        return tdee * 1.12
    raise ValueError("Unknown goal")

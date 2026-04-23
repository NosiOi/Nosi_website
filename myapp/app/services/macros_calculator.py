def calculate_macros(weight, calories, goal):
    print("DEBUG CALCULATE_MACROS CALLED")
    print("MACROS FILE:", __file__)
    if goal == "maintain":
        protein = 1.6 * weight
        fat = 1.0 * weight
    elif goal == "lose":
        protein = 2.0 * weight
        fat = 0.9 * weight
    elif goal == "gain":
        protein = 1.8 * weight
        fat = 1.0 * weight
    else:
        raise ValueError("Unknown goal")

    calories_from_protein = protein * 4
    calories_from_fat = fat * 9
    carbs = (calories - calories_from_protein - calories_from_fat) / 4

    return {
        "protein": round(protein, 1),
        "fat": round(fat, 1),
        "carbs": round(carbs, 1),
    }

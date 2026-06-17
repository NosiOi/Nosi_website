def calculate_quality(ration_items):
    if not ration_items:
        return {
            "whole_foods_percent": 0,
            "processed_foods_percent": 0,
            "fiber": 0,
            "score": 0
        }

    total_kcal = 0
    whole_kcal = 0
    fiber_total = 0

    WHOLE_FOODS = {
        "овоч", "фрукт", "круп", "рис", "греч", "вівсян",
        "м'яс", "риба", "яйц", "горіх", "бобов", "йогурт"
    }

    PROCESSED = {
        "печиво", "цукер", "шокол", "ковбас", "чіпс",
        "фаст", "сосиск", "булоч", "батонч"
    }

    for item in ration_items:
        name = (item.name or "").lower()
        kcal = item.calories or 0

        total_kcal += kcal

        if any(w in name for w in WHOLE_FOODS):
            whole_kcal += kcal

        if hasattr(item, "fiber") and item.fiber:
            fiber_total += item.fiber

    if total_kcal == 0:
        return {
            "whole_foods_percent": 0,
            "processed_foods_percent": 0,
            "fiber": 0,
            "score": 0
        }

    whole_percent = round((whole_kcal / total_kcal) * 100)
    processed_percent = 100 - whole_percent

    fiber_score = min((fiber_total / 30) * 100, 100)

    score = (
        whole_percent * 0.5 +
        (100 - processed_percent) * 0.2 +
        fiber_score * 0.3
    )

    return {
        "whole_foods_percent": whole_percent,
        "processed_foods_percent": processed_percent,
        "fiber": round(fiber_total),
        "score": round(score)
    }

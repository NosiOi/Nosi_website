from datetime import date, datetime
from myapp.app import db
from myapp.app.models import Meal, MealItem, UserGoals, NutritionPlan


def get_goals(user_id):
    goals = UserGoals.query.filter_by(user_id=user_id).first()
    if goals:
        return goals.calories_goal, goals.protein_goal, goals.fat_goal, goals.carb_goal

    base = NutritionPlan.query.filter_by(user_id=user_id).first()
    if base:
        return base.calories, base.protein, base.fats, base.carbs

    return 0, 0, 0, 0


def recalc_meal_totals(meal: Meal):
    meal.total_calories = sum(i.calories for i in meal.items)
    meal.total_protein = sum(i.protein for i in meal.items)
    meal.total_fat = sum(i.fat for i in meal.items)
    meal.total_carbs = sum(i.carbs for i in meal.items)


def calculate_quality(ration_items):
    if not ration_items:
        return {
            "whole_foods_percent": 0,
            "processed_foods_percent": 0,
            "fiber": 0,
            "score": 0
        }

    whole = 0
    processed = 0
    fiber = 0

    for item in ration_items:
        name = (item.name or "").lower()

        if any(x in name for x in ["овоч", "фрукт", "круп", "цільн", "яйц", "риба", "м'яс"]):
            whole += 1

        if any(x in name for x in ["печиво", "снек", "ковбас", "солод", "фаст"]):
            processed += 1

        if any(x in name for x in ["овоч", "фрукт", "круп", "бобов"]):
            fiber += 2

    total = whole + processed
    whole_percent = round((whole / total) * 100, 1) if total else 0
    processed_percent = round((processed / total) * 100, 1) if total else 0

    score = whole_percent - processed_percent
    score = max(0, min(100, score))

    return {
        "whole_foods_percent": whole_percent,
        "processed_foods_percent": processed_percent,
        "fiber": fiber,
        "score": score
    }


def get_daily_nutrition_data(user_id):
    from myapp.app.models import User
    from myapp.app.services.water_calculator import calculate_water

    user = User.query.get(user_id)
    today = date.today()

    meals = (
        Meal.query.filter_by(user_id=user_id, date=today)
        .order_by(Meal.time.asc().nullsfirst(), Meal.id.asc())
        .all()
    )

    total_calories = sum(m.total_calories for m in meals)
    total_protein = sum(m.total_protein for m in meals)
    total_fat = sum(m.total_fat for m in meals)
    total_carbs = sum(m.total_carbs for m in meals)

    goal_cal, goal_prot, goal_fat, goal_carb = get_goals(user_id)

    def percent(x, g):
        return round((x / g) * 100, 1) if g > 0 else 0

    progress = {
        "calories": total_calories,
        "protein": total_protein,
        "fat": total_fat,
        "carbs": total_carbs,
        "calories_percent": percent(total_calories, goal_cal),
        "protein_percent": percent(total_protein, goal_prot),
        "fat_percent": percent(total_fat, goal_fat),
        "carbs_percent": percent(total_carbs, goal_carb),
    }

    result = {
        "goal_calories": goal_cal,
        "goal_protein": goal_prot,
        "goal_fat": goal_fat,
        "goal_carbs": goal_carb,
    }

    protein = total_protein or 0
    fat = total_fat or 0
    carbs = total_carbs or 0

    total_macros = protein + fat + carbs

    if total_macros > 0:
        macros_ratio = {
            "protein": round(protein / total_macros * 100, 1),
            "fat": round(fat / total_macros * 100, 1),
            "carbs": round(carbs / total_macros * 100, 1),
        }
    else:
        macros_ratio = {"protein": 0, "fat": 0, "carbs": 0}

    ration_items = []
    for meal in meals:
        for item in meal.items:
            ration_items.append(item)

    # === RATION ITEMS ===
    ration_items = [item for meal in meals for item in meal.items]

    quality = calculate_quality(ration_items)

    # === KPI VALUES ===
    kcal = total_calories
    kcal_goal = goal_cal
    kcal_percent = progress["calories_percent"]
    kcal_balance = kcal - kcal_goal

    protein = total_protein
    protein_goal = goal_prot
    protein_percent = progress["protein_percent"]

    fat = total_fat
    fat_goal = goal_fat
    fat_percent = progress["fat_percent"]

    carb = total_carbs
    carb_goal = goal_carb
    carb_percent = progress["carbs_percent"]

    # === BALANCE STATUS ===
    if kcal_balance > 150:
        balance_status = "Перебір"
    elif kcal_balance < -150:
        balance_status = "Недобір"
    else:
        balance_status = "Норма"

    # === YESTERDAY ===
    yesterday = today.fromordinal(today.toordinal() - 1)
    meals_yesterday = Meal.query.filter_by(user_id=user_id, date=yesterday).all()

    kcal_yesterday = sum(m.total_calories for m in meals_yesterday)
    protein_yesterday = sum(m.total_protein for m in meals_yesterday)
    fat_yesterday = sum(m.total_fat for m in meals_yesterday)
    carb_yesterday = sum(m.total_carbs for m in meals_yesterday)

    def diff_label(today, yest):
        diff = today - yest
        if diff > 0:
            return f"+{diff}"
        if diff < 0:
            return f"{diff}"
        return "0"

    kcal_diff_label = diff_label(kcal, kcal_yesterday)
    protein_diff_label = diff_label(protein, protein_yesterday)
    fat_diff_label = diff_label(fat, fat_yesterday)
    carb_diff_label = diff_label(carb, carb_yesterday)

    water = calculate_water(user.weight, user.activity)
    water_goal = round(user.weight * 0.03, 2)
    water_percent = round((water / water_goal) * 100, 1) if water_goal > 0 else 0

    weekly = {
        "calorie_balance": kcal_balance,
        "avg_protein": protein,
        "avg_carbs": carb,
        "avg_fat": fat,
        "trend_label": "Стабільно",
    }

    month_avg_kcal = kcal
    month_in_target = 0
    month_max_kcal = kcal
    month_min_kcal = kcal
    month_avg_protein = protein
    month_avg_fat = fat
    month_avg_carb = carb
    month_stability_label = "Немає даних"
    current_month_label = today.strftime("%B %Y")

    day_chart = {
    "labels": [m.time.strftime("%H:%M") for m in meals],
    "kcal": [m.total_calories for m in meals],
    "protein": [m.total_protein for m in meals],
    "fat": [m.total_fat for m in meals],
    "carb": [m.total_carbs for m in meals],
    }

    from datetime import timedelta

    week_labels = []
    week_kcal = []
    week_protein = []
    week_fat = []
    week_carb = []

    for i in range(7):
        day = today - timedelta(days=i)
        meals_day = Meal.query.filter_by(user_id=user_id, date=day).all()

        week_labels.append(day.strftime("%d.%m"))
        week_kcal.append(sum(m.total_calories for m in meals_day))
        week_protein.append(sum(m.total_protein for m in meals_day))
        week_fat.append(sum(m.total_fat for m in meals_day))
        week_carb.append(sum(m.total_carbs for m in meals_day))

    week_labels.reverse()
    week_kcal.reverse()
    week_protein.reverse()
    week_fat.reverse()
    week_carb.reverse()

    week_chart = {
        "labels": week_labels,
        "kcal": week_kcal,
        "protein": week_protein,
        "fat": week_fat,
        "carb": week_carb,
    }
    first_day = today.replace(day=1)

    month_meals = Meal.query.filter(
        Meal.user_id == user_id,
        Meal.date >= first_day,
        Meal.date <= today
    ).all()

    days = {}
    for m in month_meals:
        days.setdefault(m.date, {"kcal": 0, "protein": 0, "fat": 0, "carb": 0})
        days[m.date]["kcal"] += m.total_calories
        days[m.date]["protein"] += m.total_protein
        days[m.date]["fat"] += m.total_fat
        days[m.date]["carb"] += m.total_carbs

    if not days:
        month_avg_kcal = 0
        month_in_target = 0
        month_max_kcal = 0
        month_min_kcal = 0
        month_avg_protein = 0
        month_avg_fat = 0
        month_avg_carb = 0
        month_stability_label = "Немає даних"
    else:
        kcal_values = [v["kcal"] for v in days.values()]
        protein_values = [v["protein"] for v in days.values()]
        fat_values = [v["fat"] for v in days.values()]
        carb_values = [v["carb"] for v in days.values()]

        month_avg_kcal = round(sum(kcal_values) / len(kcal_values))
        month_in_target = sum(1 for x in kcal_values if abs(x - goal_cal) <= 150)
        month_max_kcal = max(kcal_values)
        month_min_kcal = min(kcal_values)
        month_avg_protein = round(sum(protein_values) / len(protein_values))
        month_avg_fat = round(sum(fat_values) / len(fat_values))
        month_avg_carb = round(sum(carb_values) / len(carb_values))

        diff = month_max_kcal - month_min_kcal
        if diff < 200:
            month_stability_label = "Дуже стабільно"
        elif diff < 400:
            month_stability_label = "Стабільно"
        else:
            month_stability_label = "Коливається"

    current_month_label = today.strftime("%B %Y")

    return {
        "meals": meals,
        "progress": progress,
        "result": result,
        "macros_ratio": macros_ratio,
        "ration_items": ration_items,
        "quality": quality,

        "kcal": kcal,
        "kcal_goal": kcal_goal,
        "kcal_percent": kcal_percent,
        "kcal_balance": kcal_balance,

        "protein": protein,
        "protein_goal": protein_goal,
        "protein_percent": protein_percent,

        "fat": fat,
        "fat_goal": fat_goal,
        "fat_percent": fat_percent,

        "carb": carb,
        "carb_goal": carb_goal,
        "carb_percent": carb_percent,

        "balance_status": balance_status,

        "kcal_yesterday": kcal_yesterday,
        "protein_yesterday": protein_yesterday,
        "fat_yesterday": fat_yesterday,
        "carb_yesterday": carb_yesterday,

        "kcal_diff_label": kcal_diff_label,
        "protein_diff_label": protein_diff_label,
        "fat_diff_label": fat_diff_label,
        "carb_diff_label": carb_diff_label,

        "water": water,
        "water_goal": water_goal,
        "water_percent": water_percent,

        "weekly": weekly,
        "week_avg_kcal": kcal,
        "week_in_target": 0,
        "week_best_day": "—",

        "month_avg_kcal": month_avg_kcal,
        "month_in_target": month_in_target,
        "month_max_kcal": month_max_kcal,
        "month_min_kcal": month_min_kcal,
        "month_avg_protein": month_avg_protein,
        "month_avg_fat": month_avg_fat,
        "month_avg_carb": month_avg_carb,
        "month_stability_label": month_stability_label,
        "current_month_label": current_month_label,

        "day_chart": day_chart,
        "week_chart": week_chart,

        "month_avg_kcal": month_avg_kcal,
        "month_in_target": month_in_target,
        "month_max_kcal": month_max_kcal,
        "month_min_kcal": month_min_kcal,
        "month_avg_protein": month_avg_protein,
        "month_avg_fat": month_avg_fat,
        "month_avg_carb": month_avg_carb,
        "month_stability_label": month_stability_label,
        "current_month_label": current_month_label,
    }



def add_meal_service(user_id, form):
    meal = Meal(
        user_id=user_id,
        date=date.today(),
        time=form["time"],
        name=form["name"],
        category=form["category"],
        total_calories=int(form["kcal"]),
        total_protein=int(form["protein"]),
        total_fat=int(form["fat"]),
        total_carbs=int(form["carb"]),
    )

    db.session.add(meal)
    db.session.commit()



def add_item_service(user_id, form):
    meal_id = int(form["meal_id"])
    meal = Meal.query.filter_by(id=meal_id, user_id=user_id).first()
    if not meal:
        return

    item = MealItem(
        meal_id=meal.id,
        name=form["name"],
        calories=int(form.get("calories", 0)),
        protein=int(form.get("protein", 0)),
        fat=int(form.get("fat", 0)),
        carbs=int(form.get("carbs", 0)),
    )

    db.session.add(item)
    db.session.flush()

    recalc_meal_totals(meal)

    db.session.add(meal)
    db.session.commit()


def delete_meal_service(user_id, meal_id):
    meal = Meal.query.filter_by(id=meal_id, user_id=user_id).first()
    if meal:
        db.session.delete(meal)
        db.session.commit()


def delete_item_service(user_id, item_id):
    item = (
        MealItem.query.join(Meal)
        .filter(MealItem.id == item_id, Meal.user_id == user_id)
        .first()
    )
    if not item:
        return

    meal = item.meal

    db.session.delete(item)
    db.session.flush()

    recalc_meal_totals(meal)

    db.session.add(meal)
    db.session.commit()


def copy_meal_service(user_id, meal_id):
    source = Meal.query.filter_by(id=meal_id, user_id=user_id).first()
    if not source:
        return

    new_meal = Meal(
        user_id=user_id,
        date=date.today(),
        time=datetime.now().time(),
        total_calories=0,
        total_protein=0,
        total_fat=0,
        total_carbs=0,
    )

    db.session.add(new_meal)
    db.session.flush()

    for item in source.items:
        db.session.add(
            MealItem(
                meal_id=new_meal.id,
                name=item.name,
                calories=item.calories,
                protein=item.protein,
                fat=item.fat,
                carbs=item.carbs,
            )
        )

    db.session.flush()

    recalc_meal_totals(new_meal)

    db.session.commit()
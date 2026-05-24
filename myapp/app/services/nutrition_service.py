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

    ration_summary = {
        "calories": total_calories,
        "protein": total_protein,
        "fat": total_fat,
        "carbs": total_carbs,
        "calories_diff": total_calories - goal_cal,
        "protein_diff": total_protein - goal_prot,
        "fat_diff": total_fat - goal_fat,
        "carbs_diff": total_carbs - goal_carb,
    }

    weekly = {
        "calorie_balance": total_calories - goal_cal,
        "avg_protein": total_protein,
        "avg_carbs": total_carbs,
        "avg_fat": total_fat,
        "trend_label": "Стабільно"
    }

    quality = calculate_quality(ration_items)

    return {
        "meals": meals,
        "progress": progress,
        "result": result,
        "macros_ratio": macros_ratio,
        "ration_items": ration_items,
        "ration_summary": ration_summary,
        "weekly": weekly,
        "quality": quality
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

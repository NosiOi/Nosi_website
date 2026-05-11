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

    return {
        "meals": meals,
        "progress": progress,
        "result": result,
        "macros_ratio": macros_ratio,
    }


def add_meal_service(user_id):
    meal = Meal(
        user_id=user_id,
        date=date.today(),
        time=datetime.now().time(),
        total_calories=0,
        total_protein=0,
        total_fat=0,
        total_carbs=0,
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

    meal.total_calories += item.calories
    meal.total_protein += item.protein
    meal.total_fat += item.fat
    meal.total_carbs += item.carbs

    db.session.add(item)
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
    meal.total_calories -= item.calories
    meal.total_protein -= item.protein
    meal.total_fat -= item.fat
    meal.total_carbs -= item.carbs

    db.session.delete(item)
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
        total_calories=source.total_calories,
        total_protein=source.total_protein,
        total_fat=source.total_fat,
        total_carbs=source.total_carbs,
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

    db.session.commit()

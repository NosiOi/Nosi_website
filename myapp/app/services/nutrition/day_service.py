from datetime import date, timedelta

from myapp.app import db
from myapp.app.models.nutrition.meal import Meal
from myapp.app.models.nutrition.meal_item import MealItem
from myapp.app.models.nutrition.user_goals import UserGoals
from myapp.app.models.nutrition.plan import NutritionPlan
from myapp.app.models.user import User
from myapp.app.models.user_profile import UserProfile
from myapp.app.models.nutrition.user_weight import UserWeight
from myapp.app.models.nutrition.user_water import UserWater

from myapp.app.services.nutrition.quality_service import calculate_quality
from myapp.app.services.nutrition.water_service import calculate_water


def get_goals(user_id):
    goals = UserGoals.query.filter_by(user_id=user_id).first()
    if goals:
        return goals.calories_goal, goals.protein_goal, goals.fat_goal, goals.carb_goal

    base = NutritionPlan.query.filter_by(user_id=user_id).first()
    if base:
        return base.calories, base.protein, base.fats, base.carbs

    return 0, 0, 0, 0


def safe_profile_value(profile, field, default):
    if not profile:
        return default
    value = getattr(profile, field, None)
    return value if value not in (None, "") else default


def get_daily_nutrition_data(user_id):
    user = User.query.get(user_id)
    today = date.today()

    meals = (
        Meal.query.filter_by(user_id=user_id, date=today)
        .order_by(Meal.time.asc().nullsfirst(), Meal.id.asc())
        .all()
    )

    total_calories = sum(i.calories for m in meals for i in m.items)
    total_protein = sum(i.protein for m in meals for i in m.items)
    total_fat = sum(i.fat for m in meals for i in m.items)
    total_carbs = sum(i.carbs for m in meals for i in m.items)

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

    protein = total_protein
    fat = total_fat
    carbs = total_carbs

    total_macros = protein + fat + carbs
    if total_macros > 0:
        macros_ratio = {
            "protein": round(protein / total_macros * 100, 1),
            "fat": round(fat / total_macros * 100, 1),
            "carbs": round(carbs / total_macros * 100, 1),
        }
    else:
        macros_ratio = {"protein": 0, "fat": 0, "carbs": 0}

    ration_items = [
        {
            "id": item.id,
            "name": item.name,
            "calories": item.calories,
            "protein": item.protein,
            "fat": item.fat,
            "carbs": item.carbs,
        }
        for meal in meals
        for item in meal.items
    ]

    quality = calculate_quality(ration_items)

    kcal = total_calories
    kcal_goal = goal_cal
    kcal_balance = kcal - kcal_goal

    if kcal_balance > 150:
        balance_status = "Перебір"
    elif kcal_balance < -150:
        balance_status = "Недобір"
    else:
        balance_status = "Норма"

    yesterday = today - timedelta(days=1)
    meals_yesterday = Meal.query.filter_by(user_id=user_id, date=yesterday).all()

    kcal_yesterday = sum(m.total_calories for m in meals_yesterday)
    protein_yesterday = sum(m.total_protein for m in meals_yesterday)
    fat_yesterday = sum(m.total_fat for m in meals_yesterday)
    carb_yesterday = sum(m.total_carbs for m in meals_yesterday)

    def diff_label(today_val, yest_val):
        diff = today_val - yest_val
        return f"+{diff}" if diff > 0 else str(diff)

    kcal_diff_label = diff_label(kcal, kcal_yesterday)
    protein_diff_label = diff_label(protein, protein_yesterday)
    fat_diff_label = diff_label(fat, fat_yesterday)
    carb_diff_label = diff_label(carbs, carb_yesterday)

    def parse_float(value, default=0.0):
        try:
            if value is None:
                return default
            if isinstance(value, (int, float)):
                return float(value)
            value = str(value).replace(",", ".").strip()
            return float(value)
        except:
            return default

    profile = UserProfile.query.filter_by(user_id=user_id).first()

    weight = parse_float(safe_profile_value(profile, "weight", 0))
    height = parse_float(safe_profile_value(profile, "height", 170))
    age = int(parse_float(safe_profile_value(profile, "age", 25)))
    gender = safe_profile_value(profile, "gender", "male")
    activity = safe_profile_value(profile, "activity", "low")
    goal = safe_profile_value(profile, "goal", "maintain")

    try:
        water_goal = calculate_water(
            weight=weight,
            height=height,
            age=age,
            gender=gender,
            activity=activity,
            goal=goal
        )
    except:
        water_goal = 2000

    water_entry = UserWater.query.filter_by(user_id=user_id, date=today).first()
    water_today = water_entry.amount if water_entry else 0
    water_percent = round((water_today / water_goal) * 100, 1) if water_goal > 0 else 0

    weekly = {
        "calorie_balance": kcal_balance,
        "avg_protein": protein,
        "avg_carbs": carbs,
        "avg_fat": fat,
        "trend_label": "Стабільно",
    }

    day_chart = {
        "labels": [m.time.strftime("%H:%M") for m in meals if m.time],
        "kcal": [m.total_calories for m in meals],
        "protein": [m.total_protein for m in meals],
        "fat": [m.total_fat for m in meals],
        "carb": [m.total_carbs for m in meals],
    }

    week_labels = []
    week_kcal = []
    week_protein = []
    week_fat = []
    week_carb = []

    for i in range(7):
        d = today - timedelta(days=i)
        meals_day = Meal.query.filter_by(user_id=user_id, date=d).all()

        week_labels.append(d.strftime("%d.%m"))
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

    if days:
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
    else:
        month_avg_kcal = 0
        month_in_target = 0
        month_max_kcal = 0
        month_min_kcal = 0
        month_avg_protein = 0
        month_avg_fat = 0
        month_avg_carb = 0
        month_stability_label = "Немає даних"

    history_days = []
    for i in range(1, 15):
        d = today - timedelta(days=i)
        meals_day = Meal.query.filter_by(user_id=user_id, date=d).all()
        if meals_day:
            history_days.append({
                "date": d.strftime("%d.%m.%Y"),
                "total_kcal": sum(m.total_calories for m in meals_day),
                "meals": [{"name": m.name, "kcal": m.total_calories} for m in meals_day]
            })

    templates = NutritionPlan.query.filter_by(user_id=user_id).all()
    meal_templates = [{
        "id": t.id,
        "name": f"План #{t.id}",
        "kcal": t.calories,
        "protein": t.protein,
        "fat": t.fats,
        "carb": t.carbs
    } for t in templates]

    last_weight = (
        UserWeight.query.filter_by(user_id=user_id)
        .order_by(UserWeight.date.desc())
        .first()
    )
    current_weight = (
        user.profile.weight
        if user.profile and user.profile.weight is not None
        else None
    )

    return {
        "meals": [serialize_meal(m) for m in meals],
        "progress": progress,
        "result": result,
        "macros_ratio": macros_ratio,
        "ration_items": ration_items,
        "quality": quality,

        "current_weight": current_weight,

        "kcal": kcal,
        "kcal_goal": kcal_goal,
        "kcal_percent": progress["calories_percent"],
        "kcal_balance": kcal_balance,

        "protein": protein,
        "protein_goal": goal_prot,
        "protein_percent": progress["protein_percent"],

        "fat": fat,
        "fat_goal": goal_fat,
        "fat_percent": progress["fat_percent"],

        "carb": carbs,
        "carb_goal": goal_carb,
        "carb_percent": progress["carbs_percent"],

        "balance_status": balance_status,

        "kcal_yesterday": kcal_yesterday,
        "protein_yesterday": protein_yesterday,
        "fat_yesterday": fat_yesterday,
        "carb_yesterday": carb_yesterday,

        "kcal_diff_label": kcal_diff_label,
        "protein_diff_label": protein_diff_label,
        "fat_diff_label": fat_diff_label,
        "carb_diff_label": carb_diff_label,

        "water": water_today,
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
        "current_month_label": today.strftime("%B %Y"),

        "day_chart": day_chart,
        "week_chart": week_chart,

        "meals_history": history_days,
        "meal_templates": meal_templates,
    }


def serialize_meal(meal):
    return {
        "id": meal.id,
        "name": meal.name,
        "category": meal.category,
        "time": meal.time.strftime("%H:%M") if meal.time else None,
        "total_calories": meal.total_calories,
        "total_protein": meal.total_protein,
        "total_fat": meal.total_fat,
        "total_carbs": meal.total_carbs,
        "items": [
            {
                "id": item.id,
                "name": item.name,
                "calories": item.calories,
                "protein": item.protein,
                "fat": item.fat,
                "carbs": item.carbs,
            }
            for item in meal.items
        ]
    }
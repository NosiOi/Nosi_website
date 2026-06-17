from flask import Blueprint, request, jsonify
from flask_login import login_required, current_user
from datetime import date, datetime, timedelta
from myapp.app import db
from myapp.app.models.nutrition.meal import Meal
from myapp.app.models.nutrition.meal_item import MealItem
from myapp.app.models.nutrition.user_goals import UserGoals
from myapp.app.models.nutrition.user_weight_history import UserWeightHistory
from myapp.app.repositories.nutrition_repository import get_meals_for_day, get_meal_by_id, get_item_by_id

nutrition_api = Blueprint("nutrition_api", __name__, url_prefix="/nutrition")


@nutrition_api.route("/day", methods=["GET"])
@login_required
def get_day():
    d = request.args.get("date")
    d = date.fromisoformat(d) if d else date.today()
    meals = get_meals_for_day(current_user.id, d)
    total = {"calories": 0, "protein": 0, "fat": 0, "carbs": 0}
    for m in meals:
        total["calories"] += m.total_calories
        total["protein"] += m.total_protein
        total["fat"] += m.total_fat
        total["carbs"] += m.total_carbs
    goals = UserGoals.query.filter_by(user_id=current_user.id).first()
    return jsonify({"meals": [serialize_meal(m) for m in meals], "total": total, "goals": serialize_goals(goals)})


@nutrition_api.route("/add_meal", methods=["POST"])
@login_required
def add_meal():
    data = request.json
    m = Meal(
        user_id=current_user.id,
        date=date.fromisoformat(data["date"]),
        time=datetime.strptime(data["time"], "%H:%M").time() if data.get("time") else None,
        name=data["name"],
        category=data["category"],
        total_calories=0,
        total_protein=0,
        total_fat=0,
        total_carbs=0
    )
    db.session.add(m)
    db.session.commit()
    return jsonify({"meal": serialize_meal(m)})


@nutrition_api.route("/add_item", methods=["POST"])
@login_required
def add_item():
    data = request.json
    meal = get_meal_by_id(data["meal_id"], current_user.id)
    item = MealItem(
        meal_id=meal.id,
        name=data["name"],
        weight=data.get("weight"),
        calories=data["calories"],
        protein=data["protein"],
        fat=data["fat"],
        carbs=data["carbs"]
    )
    db.session.add(item)
    meal.total_calories += item.calories
    meal.total_protein += item.protein
    meal.total_fat += item.fat
    meal.total_carbs += item.carbs
    db.session.commit()
    return jsonify({"meal": serialize_meal(meal)})


@nutrition_api.route("/delete_item", methods=["POST"])
@login_required
def delete_item():
    item = get_item_by_id(request.json["item_id"], current_user.id)
    meal = item.meal
    meal.total_calories -= item.calories
    meal.total_protein -= item.protein
    meal.total_fat -= item.fat
    meal.total_carbs -= item.carbs
    db.session.delete(item)
    db.session.commit()
    return jsonify({"meal": serialize_meal(meal)})


@nutrition_api.route("/delete_meal", methods=["POST"])
@login_required
def delete_meal():
    meal = get_meal_by_id(request.json["meal_id"], current_user.id)
    db.session.delete(meal)
    db.session.commit()
    return jsonify({"status": "ok"})


@nutrition_api.route("/update_weight", methods=["POST"])
@login_required
def update_weight():
    w = float(request.json["weight"])
    entry = UserWeightHistory(user_id=current_user.id, weight=w, date=date.today())
    db.session.add(entry)
    db.session.commit()
    return jsonify({"weight": w})


@nutrition_api.route("/period", methods=["GET"])
@login_required
def get_period():
    days = int(request.args.get("days", 7))
    start = date.today() - timedelta(days=days - 1)
    meals = Meal.query.filter(Meal.user_id == current_user.id, Meal.date >= start).all()
    data = {}
    for m in meals:
        d = m.date.isoformat()
        if d not in data:
            data[d] = {"calories": 0, "protein": 0, "fat": 0, "carbs": 0}
        data[d]["calories"] += m.total_calories
        data[d]["protein"] += m.total_protein
        data[d]["fat"] += m.total_fat
        data[d]["carbs"] += m.total_carbs
    return jsonify(data)


def serialize_meal(m):
    return {
        "id": m.id,
        "name": m.name,
        "category": m.category,
        "date": m.date.isoformat(),
        "time": m.time.strftime("%H:%M") if m.time else None,
        "total": {
            "calories": m.total_calories,
            "protein": m.total_protein,
            "fat": m.total_fat,
            "carbs": m.total_carbs
        },
        "items": [serialize_item(i) for i in m.items]
    }


def serialize_item(i):
    return {
        "id": i.id,
        "name": i.name,
        "weight": i.weight,
        "calories": i.calories,
        "protein": i.protein,
        "fat": i.fat,
        "carbs": i.carbs
    }


def serialize_goals(g):
    if not g:
        return None
    return {
        "calories": g.calories_goal,
        "protein": g.protein_goal,
        "fat": g.fat_goal,
        "carbs": g.carb_goal
    }

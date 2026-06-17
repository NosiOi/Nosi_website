from flask import Blueprint, request, jsonify
from flask_login import login_required, current_user
from myapp.app import db

from myapp.app.services.nutrition_service import (
    get_daily_nutrition_data,
    add_meal_service,
    add_item_service,
    delete_meal_service,
    delete_item_service,
    copy_meal_service
)

from myapp.app.models import Meal, MealItem, UserWeight
from datetime import date, datetime, timedelta

nutrition_api = Blueprint("nutrition_api", __name__, url_prefix="/api/nutrition")


def parse_date():
    d = request.args.get("date")
    if not d:
        return date.today()
    try:
        return datetime.strptime(d, "%Y-%m-%d").date()
    except:
        return date.today()


@nutrition_api.get("/day")
@login_required
def api_day():
    d = parse_date()
    data = get_daily_nutrition_data(current_user.id)
    return jsonify(data)


@nutrition_api.post("/meals")
@login_required
def api_add_meal():
    form = request.json or {}

    required = ["name", "category"]
    if not all(k in form for k in required):
        return jsonify({"error": "Missing fields"}), 400

    add_meal_service(current_user.id, {
        "name": form["name"],
        "category": form["category"],
        "time": form.get("time"),
        "kcal": form.get("calories", 0),
        "protein": form.get("protein", 0),
        "fat": form.get("fat", 0),
        "carb": form.get("carbs", 0),
    })

    return jsonify({"status": "ok"})


@nutrition_api.put("/meals/<int:meal_id>")
@login_required
def api_edit_meal(meal_id):
    form = request.json or {}

    meal = Meal.query.filter_by(id=meal_id, user_id=current_user.id).first()
    if not meal:
        return jsonify({"error": "Not found"}), 404

    meal.name = form.get("name", meal.name)
    meal.category = form.get("category", meal.category)
    meal.time = form.get("time", meal.time)

    db.session.add(meal)
    db.session.commit()

    return jsonify({"status": "ok"})


@nutrition_api.delete("/meals/<int:meal_id>")
@login_required
def api_delete_meal(meal_id):
    delete_meal_service(current_user.id, meal_id)
    return jsonify({"status": "ok"})


@nutrition_api.post("/items")
@login_required
def api_add_item():
    form = request.json or {}

    required = ["meal_id", "name"]
    if not all(k in form for k in required):
        return jsonify({"error": "Missing fields"}), 400

    add_item_service(current_user.id, {
        "meal_id": form["meal_id"],
        "name": form["name"],
        "calories": form.get("calories", 0),
        "protein": form.get("protein", 0),
        "fat": form.get("fat", 0),
        "carbs": form.get("carbs", 0),
    })

    return jsonify({"status": "ok"})


@nutrition_api.put("/items/<int:item_id>")
@login_required
def api_edit_item(item_id):
    form = request.json or {}

    item = (
        MealItem.query.join(Meal)
        .filter(MealItem.id == item_id, Meal.user_id == current_user.id)
        .first()
    )
    if not item:
        return jsonify({"error": "Not found"}), 404

    item.name = form.get("name", item.name)
    item.calories = form.get("calories", item.calories)
    item.protein = form.get("protein", item.protein)
    item.fat = form.get("fat", item.fat)
    item.carbs = form.get("carbs", item.carbs)

    db.session.add(item)
    db.session.commit()

    return jsonify({"status": "ok"})


@nutrition_api.delete("/items/<int:item_id>")
@login_required
def api_delete_item(item_id):
    delete_item_service(current_user.id, item_id)
    return jsonify({"status": "ok"})


@nutrition_api.post("/copy_yesterday")
@login_required
def api_copy_yesterday():
    today = date.today()
    yesterday = today - timedelta(days=1)

    meals = Meal.query.filter_by(user_id=current_user.id, date=yesterday).all()
    if not meals:
        return jsonify({"error": "No meals yesterday"}), 400

    for m in meals:
        copy_meal_service(current_user.id, m.id)

    return jsonify({"status": "ok"})


@nutrition_api.post("/weight")
@login_required
def api_update_weight():
    form = request.json or {}
    w = form.get("weight")

    if not w:
        return jsonify({"error": "Missing weight"}), 400

    entry = UserWeight(
        user_id=current_user.id,
        date=date.today(),
        weight=float(w)
    )

    db.session.add(entry)
    db.session.commit()

    return jsonify({"status": "ok"})


@nutrition_api.get("/stats")
@login_required
def api_stats():
    days = int(request.args.get("days", 7))
    today = date.today()

    labels = []
    kcal = []
    weight_labels = []
    weight_values = []

    for i in range(days):
        d = today - timedelta(days=i)
        meals = Meal.query.filter_by(user_id=current_user.id, date=d).all()
        labels.append(d.strftime("%d.%m"))
        kcal.append(sum(m.total_calories for m in meals))

    labels.reverse()
    kcal.reverse()

    weights = (
        UserWeight.query.filter_by(user_id=current_user.id)
        .order_by(UserWeight.date.asc())
        .all()
    )

    for w in weights:
        weight_labels.append(w.date.strftime("%d.%m"))
        weight_values.append(w.weight)

    return jsonify({
        "kcal": {
            "labels": labels,
            "values": kcal
        },
        "weight": {
            "labels": weight_labels,
            "values": weight_values
        },
        "avg_kcal": sum(kcal) // len(kcal) if kcal else 0,
        "goal_kcal": get_daily_nutrition_data(current_user.id)["kcal_goal"],
        "current_weight": weight_values[-1] if weight_values else None,
        "weight_trend": "Стабільно"
    })

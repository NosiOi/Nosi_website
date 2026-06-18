from flask import Blueprint, request, jsonify
from flask_login import login_required, current_user
from datetime import date, datetime, timedelta

from myapp.app import db
from myapp.app.models import Meal, MealItem, UserWeight

from myapp.app.services.nutrition.day_service import get_daily_nutrition_data
from myapp.app.services.nutrition.meal_service import (
    add_meal_service,
    delete_meal_service,
    copy_meal_service
)
from myapp.app.services.nutrition.item_service import (
    add_item_service,
    delete_item_service
)
from myapp.app.services.nutrition.stats_service import get_stats, get_year_heatmap
from myapp.app.models.nutrition.user_water import UserWater


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
    data = get_daily_nutrition_data(current_user.id)
    return jsonify(data)


@nutrition_api.post("/meals")
@login_required
def api_add_meal():
    form = request.json or {}

    if "name" not in form or "category" not in form:
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

    if "meal_id" not in form or "name" not in form:
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

    user = current_user
    user.weight = float(w)
    db.session.add(user)

    db.session.commit()

    return jsonify({"status": "ok"})


@nutrition_api.get("/stats")
@login_required
def api_stats():
    days = int(request.args.get("days", 7))
    data = get_stats(current_user.id, days)
    return jsonify(data)


@nutrition_api.get("/heatmap")
@login_required
def api_heatmap():
    y = request.args.get("year")
    try:
        year = int(y) if y else date.today().year
    except:
        year = date.today().year

    data = get_year_heatmap(current_user.id, year)
    return jsonify(data)


@nutrition_api.post("/water")
@login_required
def api_add_water():
    form = request.json or {}
    amount = form.get("amount")

    if not amount:
        return jsonify({"error": "Missing amount"}), 400

    today = date.today()

    entry = UserWater.query.filter_by(user_id=current_user.id, date=today).first()
    if not entry:
        entry = UserWater(user_id=current_user.id, date=today, amount=0)
        db.session.add(entry)

    entry.amount += float(amount)
    db.session.commit()

    return jsonify({"status": "ok"})

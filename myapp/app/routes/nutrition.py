from flask import Blueprint, render_template, session, redirect, request
from myapp.app.utils.decorators import login_required
from myapp.app.models.user import User
from myapp.app.services.nutrition_service import (
    get_daily_nutrition_data,
    add_meal_service,
    add_item_service,
    delete_meal_service,
    delete_item_service,
    copy_meal_service,
)

nutrition_bp = Blueprint("nutrition", __name__)


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
        category = (item.category_label or "").lower()

        if any(x in category for x in ["овоч", "фрукт", "круп", "цільн", "яйц", "риба", "м'яс"]):
            whole += 1

        if any(x in category for x in ["печиво", "снек", "ковбас", "солод", "фаст"]):
            processed += 1

        if any(x in category for x in ["овоч", "фрукт", "круп", "бобов"]):
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


@nutrition_bp.route("/nutrition")
@login_required
def nutrition_page():
    user_id = session["user"]
    user = User.query.get(user_id)

    data = get_daily_nutrition_data(user_id)
    data["user"] = user

    return render_template("app/nutrition.html", **data)


@nutrition_bp.route("/nutrition/add_meal", methods=["POST"])
@login_required
def add_meal():
    add_meal_service(session["user"], request.form)
    return redirect("/nutrition")



@nutrition_bp.route("/nutrition/add_item", methods=["POST"])
@login_required
def add_item():
    add_item_service(session["user"], request.form)
    return redirect("/nutrition")


@nutrition_bp.route("/nutrition/delete_meal", methods=["POST"])
@login_required
def delete_meal():
    delete_meal_service(session["user"], request.form["meal_id"])
    return redirect("/nutrition")


@nutrition_bp.route("/nutrition/delete_item", methods=["POST"])
@login_required
def delete_item():
    delete_item_service(session["user"], request.form["item_id"])
    return redirect("/nutrition")


@nutrition_bp.route("/nutrition/copy_meal", methods=["POST"])
@login_required
def copy_meal():
    copy_meal_service(session["user"], request.form["meal_id"])
    return redirect("/nutrition")

from flask import Blueprint, render_template, redirect, request
from flask_login import login_required, current_user
from myapp.app.services.nutrition_service import (
    get_daily_nutrition_data,
    add_meal_service,
    add_item_service,
    delete_meal_service,
    delete_item_service,
    copy_meal_service,
)

nutrition_bp = Blueprint("nutrition", __name__)


@nutrition_bp.route("/nutrition")
@login_required
def nutrition_page():
    user = current_user
    data = get_daily_nutrition_data(user.id)
    data["user"] = user
    return render_template("app/nutrition.html", **data)


@nutrition_bp.route("/nutrition/add_meal", methods=["POST"])
@login_required
def add_meal():
    add_meal_service(current_user.id, request.form)
    return redirect("/nutrition")


@nutrition_bp.route("/nutrition/add_item", methods=["POST"])
@login_required
def add_item():
    add_item_service(current_user.id, request.form)
    return redirect("/nutrition")


@nutrition_bp.route("/nutrition/delete_meal", methods=["POST"])
@login_required
def delete_meal():
    delete_meal_service(current_user.id, request.form["meal_id"])
    return redirect("/nutrition")


@nutrition_bp.route("/nutrition/delete_item", methods=["POST"])
@login_required
def delete_item():
    delete_item_service(current_user.id, request.form["item_id"])
    return redirect("/nutrition")


@nutrition_bp.route("/nutrition/copy_meal", methods=["POST"])
@login_required
def copy_meal():
    copy_meal_service(current_user.id, request.form["meal_id"])
    return redirect("/nutrition")

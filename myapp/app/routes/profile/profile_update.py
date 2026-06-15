from flask import Blueprint, request, jsonify
from flask_login import login_required, current_user
from myapp.app import db

profile_update_bp = Blueprint("profile_update", __name__)

@profile_update_bp.route("/profile/update_name", methods=["POST"])
@login_required
def update_name():
    data = request.json

    username = data.get("username")
    full_name = data.get("full_name")

    if username:
        current_user.username = username

    if full_name:
        current_user.full_name = full_name

    db.session.commit()

    return jsonify({
        "status": "success",
        "username": current_user.username,
        "full_name": current_user.full_name
    })


@profile_update_bp.route("/profile/update_body", methods=["POST"])
@login_required
def update_body():
    data = request.json

    if data.get("age") is not None:
        current_user.age = int(data.get("age"))

    if data.get("height") is not None:
        current_user.height_cm = float(data.get("height"))

    if data.get("weight") is not None:
        current_user.weight_kg = float(data.get("weight"))

    if data.get("target_weight") is not None:
        current_user.target_weight_kg = float(data.get("target_weight"))

    if data.get("gender") is not None:
        current_user.gender = data.get("gender")

    if data.get("activity_level") is not None:
        current_user.activity_level = data.get("activity_level")

    if data.get("goal_type") is not None:
        current_user.goal_type = data.get("goal_type")

    if data.get("waist") is not None:
        current_user.waist_cm = float(data.get("waist"))

    db.session.commit()

    return jsonify({"status": "success"})

@profile_update_bp.route("/profile/update_goal", methods=["POST"])
@login_required
def update_goal():
    data = request.json

    if data.get("main_goal") is not None:
        current_user.main_goal = data.get("main_goal")

    if data.get("workouts_per_week") is not None:
        current_user.workouts_per_week = int(data.get("workouts_per_week"))

    if data.get("workout_focus") is not None:
        current_user.workout_focus = data.get("workout_focus")

    if data.get("calories_target") is not None:
        current_user.calories_target = int(data.get("calories_target"))

    if data.get("nutrition_focus") is not None:
        current_user.nutrition_focus = data.get("nutrition_focus")

    if data.get("sleep_target_hours") is not None:
        current_user.sleep_target_hours = float(data.get("sleep_target_hours"))

    if data.get("recovery_focus") is not None:
        current_user.recovery_focus = data.get("recovery_focus")

    db.session.commit()

    return jsonify({"status": "success"})


@profile_update_bp.route("/profile/change_email", methods=["POST"])
@login_required
def change_email():
    data = request.json

    new_email = data.get("new_email")
    password = data.get("password")

    if not current_user.check_password(password):
        return jsonify({"status": "error", "message": "Невірний пароль"}), 400

    current_user.email = new_email
    db.session.commit()

    return jsonify({"status": "success", "email": new_email})


@profile_update_bp.route("/profile/change_password", methods=["POST"])
@login_required
def change_password():
    data = request.json

    current_password = data.get("current_password")
    new_password = data.get("new_password")

    if not current_user.check_password(current_password):
        return jsonify({"status": "error", "message": "Невірний пароль"}), 400

    current_user.set_password(new_password)
    db.session.commit()

    return jsonify({"status": "success"})


@profile_update_bp.route("/profile/delete_account", methods=["POST"])
@login_required
def delete_account():
    data = request.json

    confirm_email = data.get("confirm_email")
    password = data.get("password")

    if confirm_email != current_user.email:
        return jsonify({"status": "error", "message": "Email не співпадає"}), 400

    if not current_user.check_password(password):
        return jsonify({"status": "error", "message": "Невірний пароль"}), 400

    db.session.delete(current_user)
    db.session.commit()

    return jsonify({"status": "success"})

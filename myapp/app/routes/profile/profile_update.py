from flask import Blueprint, request, jsonify
from flask_login import login_required, current_user
from myapp.app import db

profile_update_bp = Blueprint("profile_update", __name__)

@profile_update_bp.route("/profile/update_name", methods=["POST"])
@login_required
def update_name():
    data = request.json
    current_user.username = data.get("username")
    db.session.commit()
    return jsonify({"status": "success", "username": current_user.username})

@profile_update_bp.route("/profile/update_body", methods=["POST"])
@login_required
def update_body():
    data = request.json
    current_user.age = int(data.get("age"))
    current_user.height = float(data.get("height"))
    current_user.weight = float(data.get("weight"))
    current_user.gender = data.get("gender")
    db.session.commit()
    return jsonify({"status": "success"})

@profile_update_bp.route("/profile/update_goal", methods=["POST"])
@login_required
def update_goal():
    data = request.json
    current_user.goal = data.get("goal")
    current_user.activity = float(data.get("activity"))
    current_user.experience = data.get("experience")
    current_user.workouts_per_week = int(data.get("workouts_per_week"))
    db.session.commit()
    return jsonify({"status": "success"})

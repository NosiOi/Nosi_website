from flask import Blueprint, request, jsonify
from myapp.app.services.plan_generator import PlanGenerator

plan_api = Blueprint("plan_api", __name__, url_prefix="/api")


@plan_api.route("/plan", methods=["POST"])
def generate_plan():
    data = request.get_json()

    # 1. Дістаємо дані з JSON
    age = data.get("age")
    gender = data.get("gender")
    weight = data.get("weight")
    height = data.get("height")
    activity = data.get("activity")
    goal = data.get("goal")
    experience = data.get("experience")
    workouts_per_week = data.get("workouts_per_week")

    # 2. Створюємо генератор плану
    generator = PlanGenerator(
        age=age,
        gender=gender,
        weight=weight,
        height=height,
        activity=activity,
        goal=goal,
        experience=experience,
        workouts_per_week=workouts_per_week,
    )

    # 3. Генеруємо план
    plan = generator.generate()

    # 4. Повертаємо JSON
    return jsonify(plan), 200

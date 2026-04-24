from flask import Blueprint, request, jsonify
from myapp.app.services.plan_generator import PlanGenerator

plan_api = Blueprint("plan_api", __name__, url_prefix="/api")


@plan_api.route("/plan", methods=["POST"])
def generate_plan_api():
    data = request.get_json()

    generator = PlanGenerator(
        age=data.get("age"),
        sex=data.get("gender"),
        weight=data.get("weight"),
        height=data.get("height"),
        activity=data.get("activity"),
        goal=data.get("goal"),
        experience=data.get("experience"),
        workouts_per_week=data.get("workouts_per_week"),
    )

    plan = generator.generate()

    return jsonify(plan), 200

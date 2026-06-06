from flask import Blueprint, render_template, jsonify
from flask_login import login_required, current_user

from myapp.app.services.training_engine_service import TrainingEngineService

plan_bp = Blueprint("plan", __name__, url_prefix="/plan")


@plan_bp.get("/view")
@login_required
def view_plan():
    plan = TrainingEngineService.generate_plan(current_user, week=1)
    return render_template("app/plan.html", plan=plan.to_dict(), user=current_user)


@plan_bp.get("/json")
@login_required
def view_plan_json():
    plan = TrainingEngineService.generate_plan(current_user, week=1)
    return jsonify(plan.to_dict())

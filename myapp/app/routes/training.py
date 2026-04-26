from flask import Blueprint, render_template
from flask_login import login_required, current_user
from myapp.app.models.training_plan import TrainingPlan
import json

training_bp = Blueprint("training", __name__)


@training_bp.route("/training")
@login_required
def training_plan():
    plan = (
        TrainingPlan.query.filter_by(user_id=current_user.id)
        .order_by(TrainingPlan.id.desc())
        .first()
    )

    if not plan:
        return "План ще не створено. Пройди тести."

    plan_data = json.loads(plan.plan_json)

    return render_template("training_plan.html", plan=plan_data)

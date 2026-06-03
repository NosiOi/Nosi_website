from flask import Blueprint, render_template, redirect
from flask_login import login_required, current_user
from myapp.app.models import WorkoutPlan

training_bp = Blueprint("training", __name__, url_prefix="/training")


@training_bp.route("/")
@login_required
def training_overview():
    user = current_user
    workout = WorkoutPlan.query.filter_by(user_id=user.id).first()

    if not workout or not workout.plan:
        return redirect("/plan/generate")

    return render_template(
        "app/training_overview.html",
        user=user,
        training_plan=workout.plan
    )

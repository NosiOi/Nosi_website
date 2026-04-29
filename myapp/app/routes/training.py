from flask import Blueprint, render_template, session, redirect
from myapp.app.models import User, WorkoutPlan

training_bp = Blueprint("training", __name__, url_prefix="/training")


@training_bp.route("/")
def training_overview():
    if "user" not in session:
        return redirect("/auth/login")

    user = User.query.get(session["user"])
    workout = WorkoutPlan.query.filter_by(user_id=user.id).first()

    if not workout or not workout.plan:
        return redirect("/plan/generate")

    return render_template(
        "app/training_overview.html", user=user, training_plan=workout.plan
    )

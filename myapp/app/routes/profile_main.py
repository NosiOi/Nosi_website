from flask import Blueprint, render_template, session, redirect, request
from flask_login import login_required, current_user
from myapp.app.models import User
from myapp.app import db

profile_bp = Blueprint("profile", __name__)


@profile_bp.route("/profile")
@login_required
def profile():
    user = User.query.get(session["user"])
    return render_template("profile.html", user=user)


@profile_bp.route("/equipment")
@login_required
def equipment_page():
    from myapp.app.models.equipment import Equipment
    from myapp.app.models.user_equipment import UserEquipment

    all_equipment = Equipment.query.all()
    user_eq_ids = [
        ue.equipment_id for ue in UserEquipment.query.filter_by(user_id=current_user.id)
    ]

    return render_template(
        "profile/equipment.html",
        equipment=all_equipment,
        user_equipment_ids=user_eq_ids,
    )


@profile_bp.route("/profile/edit", methods=["GET", "POST"])
@login_required
def edit_profile():
    user = User.query.get(session["user"])

    if request.method == "POST":
        user.username = request.form["username"]
        user.email = request.form["email"]
        user.age = int(request.form["age"])
        user.height = float(request.form["height"])
        user.weight = float(request.form["weight"])
        user.gender = request.form["gender"]
        user.activity = float(request.form["activity"])
        user.goal = request.form["goal"]
        user.experience = request.form["experience"]
        user.workouts_per_week = int(request.form["workouts_per_week"])

        if "environment" in request.form:
            user.environment = request.form["environment"]

        if "aesthetic_focus" in request.form:
            user.aesthetic_focus = request.form["aesthetic_focus"]

        if "performance_focus" in request.form:
            user.performance_focus = request.form["performance_focus"]

        if "weak_points" in request.form:
            user.weak_points = request.form.getlist("weak_points")

        if "strong_points" in request.form:
            user.strong_points = request.form.getlist("strong_points")

        db.session.commit()

        return redirect("/profile")

    return render_template("app/profile_edit.html", user=user)

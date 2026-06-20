from flask import Blueprint, render_template, redirect, request
from flask_login import login_required, current_user
from myapp.app import db
from myapp.app.models.user_profile import UserProfile

profile_bp = Blueprint("profile", __name__)


@profile_bp.route("/profile")
@login_required
def profile():
    return render_template("profile.html", user=current_user, profile=current_user.profile)


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
    user = current_user
    profile = current_user.profile

    if request.method == "POST":
        user.username = request.form["username"]
        user.email = request.form["email"]

        profile.age = int(request.form["age"])
        profile.height = float(request.form["height"])
        profile.weight = float(request.form["weight"])
        profile.gender = request.form["gender"]
        profile.activity = request.form["activity"]
        profile.goal = request.form["goal"]
        profile.experience = request.form["experience"]
        profile.workouts_per_week = int(request.form["workouts_per_week"])

        if "environment" in request.form:
            profile.training_location = request.form["environment"]

        db.session.commit()

        return redirect("/profile")

    return render_template("app/profile_edit.html", user=user, profile=profile)

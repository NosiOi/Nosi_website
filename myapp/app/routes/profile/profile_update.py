from flask import Blueprint, request, redirect, url_for, flash
from flask_login import login_required, current_user
from myapp.app import db

profile_update_bp = Blueprint("profile_update", __name__)

@profile_update_bp.route("/profile/update_full", methods=["POST"])
@login_required
def update_full():
    user = current_user

    user.username = request.form.get("username")
    user.email = request.form.get("email")
    user.age = request.form.get("age")
    user.height = request.form.get("height")
    user.weight = request.form.get("weight")
    user.gender = request.form.get("gender")
    user.activity = request.form.get("activity")
    user.goal = request.form.get("goal")
    user.experience = request.form.get("experience")
    user.workouts_per_week = request.form.get("workouts_per_week")

    if not user.profile:
        from myapp.app.models.user_profile import UserProfile
        user.profile = UserProfile(user_id=user.id)

    user.profile.training_location = request.form.get("training_location")
    user.profile.wants_nutrition = bool(int(request.form.get("wants_nutrition", 0)))
    user.profile.wants_recovery = bool(int(request.form.get("wants_recovery", 0)))
    user.profile.onboarding_completed = bool(int(request.form.get("onboarding_completed", 0)))

    db.session.commit()

    return redirect("/profile")


@profile_update_bp.route("/profile/change_email", methods=["POST"])
@login_required
def change_email():
    new_email = request.form.get("new_email")
    password = request.form.get("password")

    if not current_user.check_password(password):
        flash("Невірний пароль", "error")
        return redirect(url_for("dashboard.profile_page"))

    current_user.email = new_email
    db.session.commit()

    flash("Email оновлено", "success")
    return redirect(url_for("dashboard.profile_page"))


@profile_update_bp.route("/profile/change_password", methods=["POST"])
@login_required
def change_password():
    current_password = request.form.get("current_password")
    new_password = request.form.get("new_password")

    if not current_user.check_password(current_password):
        flash("Невірний пароль", "error")
        return redirect(url_for("dashboard.profile_page"))

    current_user.set_password(new_password)
    db.session.commit()

    flash("Пароль змінено", "success")
    return redirect(url_for("dashboard.profile_page"))


@profile_update_bp.route("/profile/delete_account", methods=["POST"])
@login_required
def delete_account():
    confirm_email = request.form.get("confirm_email")
    password = request.form.get("password")

    if confirm_email != current_user.email:
        flash("Email не співпадає", "error")
        return redirect(url_for("dashboard.profile_page"))

    if not current_user.check_password(password):
        flash("Невірний пароль", "error")
        return redirect(url_for("dashboard.profile_page"))

    db.session.delete(current_user)
    db.session.commit()

    flash("Акаунт видалено", "success")
    return redirect(url_for("auth.login"))

from flask import Blueprint, request, redirect, url_for, flash
from flask_login import login_required, current_user
from myapp.app import db

profile_update_bp = Blueprint("profile_update", __name__)

@profile_update_bp.route("/profile/update_name", methods=["POST"])
@login_required
def update_name():
    username = request.form.get("username")

    if username:
        current_user.username = username

    db.session.commit()
    flash("Ім’я оновлено", "success")
    return redirect(url_for("dashboard.profile_page"))


@profile_update_bp.route("/profile/update_body", methods=["POST"])
@login_required
def update_body():
    age = request.form.get("age")
    height = request.form.get("height")
    weight = request.form.get("weight")
    gender = request.form.get("gender")

    if age:
        current_user.age = int(age)

    if height:
        current_user.height = float(height)

    if weight:
        current_user.weight = float(weight)

    if gender:
        current_user.gender = gender

    db.session.commit()
    flash("Параметри тіла оновлено", "success")
    return redirect(url_for("dashboard.profile_page"))


@profile_update_bp.route("/profile/update_goal", methods=["POST"])
@login_required
def update_goal():
    goal = request.form.get("goal")
    activity = request.form.get("activity")
    experience = request.form.get("experience")
    workouts = request.form.get("workouts_per_week")

    if goal:
        current_user.goal = goal

    if activity:
        current_user.activity = float(activity)

    if experience:
        current_user.experience = experience

    if workouts:
        current_user.workouts_per_week = int(workouts)

    db.session.commit()
    flash("Цілі оновлено", "success")
    return redirect(url_for("dashboard.profile_page"))


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

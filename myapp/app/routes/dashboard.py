from flask import Blueprint, render_template, redirect
from flask_login import login_required, current_user

dashboard_bp = Blueprint("dashboard", __name__, url_prefix="/dashboard")


@dashboard_bp.route("/")
@login_required
def dashboard():
    return render_template("app/dashboard.html", user=current_user)


@dashboard_bp.route("/training")
@login_required
def training_page():
    return render_template("app/training/training.html", user=current_user)


@dashboard_bp.route("/nutrition")
@login_required
def nutrition_page():
    return render_template("app/nutrition/nutrition.html")


@dashboard_bp.route("/recovery")
@login_required
def recovery_page():
    return render_template("app/recovery.html", user=current_user)


@dashboard_bp.route("/assessment")
@login_required
def assessment_page():
    return render_template("app/assessment.html", user=current_user)


@dashboard_bp.route("/equipment")
@login_required
def equipment_page():
    return render_template("app/equipment.html", user=current_user)


@dashboard_bp.route("/training_plan")
@login_required
def training_plan_page():
    return render_template("app/training_plan.html", user=current_user)


@dashboard_bp.route("/training_explanation")
@login_required
def training_explanation_page():
    return render_template("app/training/explanation.html", user=current_user)


@dashboard_bp.route("/profile")
@login_required
def profile_page():
    return render_template(
        "app/profile/profile.html",
        user=current_user,
        profile=current_user.profile
    )


@dashboard_bp.route("/questionnaire")
@login_required
def questionnaire_page():
    return render_template("app/questionnaire.html", user=current_user)


@dashboard_bp.route("/tracker")
@login_required
def tracker_page():
    return render_template("app/tracker.html", user=current_user)

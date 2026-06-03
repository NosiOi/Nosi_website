from flask import Blueprint, render_template, session, redirect
from flask_login import login_required, current_user
from myapp.app.models import User

dashboard_bp = Blueprint("dashboard", __name__)


@dashboard_bp.route("/")
def index():
    return render_template("public/landing.html")


@dashboard_bp.route("/dashboard")
@login_required
def dashboard():
    user = current_user

    return render_template("app/dashboard.html", user=user)


@dashboard_bp.route("/demo")
def demo():
    return render_template("public/demo.html")


@dashboard_bp.route("/about")
def about():
    return render_template("public/about.html")


@dashboard_bp.route("/pricing")
def pricing():
    return render_template("public/pricing.html")


@dashboard_bp.route("/sport")
@login_required
def sport_page():
    user = current_user
    return render_template("app/sport.html", user=user)



@dashboard_bp.route("/recovery")
@login_required
def recovery_page():
    user = current_user
    return render_template("app/recovery.html", user=user)


@dashboard_bp.route("/assessment")
@login_required
def assessment_page():
    user = current_user
    return render_template("app/assessment.html", user=user)


@dashboard_bp.route("/equipment")
@login_required
def equipment_page():
    user = current_user
    return render_template("app/equipment.html", user=user)


@dashboard_bp.route("/training_plan")
@login_required
def training_plan_page():
    user = current_user
    return render_template("app/training_plan.html", user=user)


@dashboard_bp.route("/training_explanation")
@login_required
def training_explanation_page():
    user = current_user
    return render_template("app/training_explanation.html", user=user)


@dashboard_bp.route("/profile")
@login_required
def profile_page():
    user = current_user
    return render_template("app/profile.html", user=user)


@dashboard_bp.route("/questionnaire")
@login_required
def questionnaire_page():
    user = current_user
    return render_template("app/questionnaire.html", user=user)

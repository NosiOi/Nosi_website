from flask import Blueprint, render_template, session, redirect
from myapp.app.models import User

dashboard_bp = Blueprint("dashboard", __name__)


@dashboard_bp.route("/")
def index():
    return render_template("landing.html")


@dashboard_bp.route("/dashboard")
def dashboard():
    if "user" not in session:
        return redirect("/login")

    user = User.query.get(session["user"])
    return render_template("dashboard.html", user=user)


@dashboard_bp.route("/account")
def account():
    if "user" not in session:
        return redirect("/login")

    user = User.query.get(session["user"])
    return render_template("account.html", user=user)


@dashboard_bp.route("/sport")
def sport():
    return render_template("sport.html")


@dashboard_bp.route("/diet_page")
def diet_page():
    return render_template("diet_page.html")


@dashboard_bp.route("/recovery")
def recovery_page():
    return render_template("recovery.html")

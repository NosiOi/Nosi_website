from flask import Blueprint, render_template, request, redirect, flash, session, url_for, current_app
from werkzeug.security import generate_password_hash, check_password_hash
from flask_login import login_user, logout_user
from myapp.app import db
from myapp.app.models.user import User

auth_bp = Blueprint("auth", __name__, url_prefix="/auth")
print("LOADED AUTH_MAIN:", __file__)


@auth_bp.route("/login", methods=["GET", "POST"], endpoint="login")
def login():
    if request.method == "POST":
        email = request.form.get("email")
        password = request.form.get("password")

        user = User.query.filter_by(email=email).first()

        if not user:
            flash("Користувача не знайдено", "error")
            return redirect(url_for("auth.login"))

        if not check_password_hash(user.password, password):
            flash("Невірний пароль", "error")
            return redirect(url_for("auth.login"))

        login_user(user, remember=True)
        return redirect(url_for("dashboard.dashboard"))

    return render_template("auth/login.html")


@auth_bp.route("/register", methods=["GET"], endpoint="register")
def register():
    return render_template("auth/register.html")


@auth_bp.route("/register_complete", methods=["GET", "POST"], endpoint="register_complete")
def register_complete():
    reg_data = session.get("reg_data")
    verified_email = session.get("verified_email")

    if not reg_data or not verified_email:
        flash("Спочатку підтвердіть email", "error")
        return redirect(url_for("auth.register"))

    if request.method == "POST":
        hashed_password = generate_password_hash(reg_data["password"])

        user = User(
            username=reg_data["username"],
            email=verified_email,
            password=hashed_password,
            age=int(reg_data.get("age", 0)) if reg_data.get("age") else None,
            height=float(reg_data.get("height", 0)) if reg_data.get("height") else None,
            weight=float(reg_data.get("weight", 0)) if reg_data.get("weight") else None,
            gender=reg_data.get("gender"),
            activity=float(reg_data.get("activity")) if reg_data.get("activity") else None,
            goal=reg_data.get("goal"),
            experience=reg_data.get("experience"),
            workouts_per_week=int(reg_data.get("workouts_per_week", 0)) if reg_data.get("workouts_per_week") else None,
        )

        db.session.add(user)
        db.session.commit()

        session.pop("reg_data", None)
        session.pop("verified_email", None)

        login_user(user, remember=True)
        return redirect(url_for("dashboard.dashboard"))

    return render_template("auth/register_complete.html")


@auth_bp.route("/logout", endpoint="logout")
def logout():
    logout_user()
    return redirect(url_for("root.landing"))


@auth_bp.route("/reset", methods=["GET", "POST"], endpoint="reset_password")
def reset_password():
    if request.method == "POST":
        email = request.form.get("email")
        flash("Якщо адреса існує в системі, лист з інструкцією буде надіслано.", "info")
        return redirect(url_for("auth.login"))
    return render_template("auth/reset_password.html")


@auth_bp.route("/forgot", endpoint="forgot")
def forgot_alias():
    return redirect(url_for("auth.reset_password"))

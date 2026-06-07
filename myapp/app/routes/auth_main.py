from flask import Blueprint, render_template, request, redirect, flash, session
from werkzeug.security import generate_password_hash, check_password_hash
from flask_login import login_user, logout_user
from myapp.app import db
from myapp.app.models.user import User

auth_bp = Blueprint("auth", __name__, url_prefix="/auth")
print("LOADED AUTH_MAIN:", __file__)


@auth_bp.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        email = request.form.get("email")
        password = request.form.get("password")

        user = User.query.filter_by(email=email).first()

        if not user:
            flash("Користувача не знайдено", "error")
            return redirect("/auth/login")

        if not check_password_hash(user.password, password):
            flash("Невірний пароль", "error")
            return redirect("/auth/login")

        login_user(user, remember=True)
        return redirect("/dashboard")

    return render_template("auth/login.html")


@auth_bp.route("/register", methods=["GET"])
def register():
    return render_template("auth/register.html")


@auth_bp.route("/register_complete", methods=["GET", "POST"])
def register_complete():
    reg_data = session.get("reg_data")
    print("REG DATA:", reg_data)
    verified_email = session.get("verified_email")
    print("VERIFIED EMAIL:", verified_email)

    if not reg_data or not verified_email:
        flash("Спочатку підтвердіть email", "error")
        return redirect("/auth/register")

    if request.method == "POST":
        hashed_password = generate_password_hash(reg_data["password"])

        user = User(
            username=reg_data["username"],
            email=verified_email,
            password=hashed_password,
            age=int(reg_data["age"]),
            height=float(reg_data["height"]),
            weight=float(reg_data["weight"]),
            gender=reg_data["gender"],
            activity=float(reg_data["activity"]),
            goal=reg_data["goal"],
            experience=reg_data["experience"],
            workouts_per_week=int(reg_data["workouts_per_week"]),
        )

        db.session.add(user)
        db.session.commit()

        session.pop("reg_data", None)
        session.pop("verified_email", None)

        login_user(user, remember=True)
        return redirect("/dashboard")

    return render_template("auth/register_complete.html")


@auth_bp.route("/logout")
def logout():
    logout_user()
    return redirect("/")

from flask import Blueprint, render_template, request, redirect
from werkzeug.security import generate_password_hash, check_password_hash
from myapp.app import db
from myapp.app.models import User

auth_bp = Blueprint("auth", __name__, url_prefix="/auth")


@auth_bp.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        email = request.form["email"]
        password = request.form["password"]

        user = User.query.filter_by(email=email).first()

        if not user:
            return "Користувача не знайдено"

        if not check_password_hash(user.password, password):
            return "Невірний пароль"

        from flask_login import login_user
        login_user(user)
        return redirect("/dashboard")


    return render_template("auth/login.html")


@auth_bp.route("/register", methods=["GET", "POST"])
def register():
    if request.method == "POST":
        username = request.form["username"]
        email = request.form["email"]
        password = request.form["password"]
        age = int(request.form["age"])
        height = int(request.form["height"])
        weight = int(request.form["weight"])
        gender = request.form["gender"]
        activity = float(request.form.get("activity"))

        if User.query.filter_by(email=email).first():
            return "Користувач з такою поштою вже існує"

        hashed_password = generate_password_hash(password)

        user = User(
            username=username,
            email=email,
            password=hashed_password,
            age=age,
            height=height,
            weight=weight,
            gender=gender,
            activity=activity,
            goal=request.form.get("goal"),
            experience=request.form.get("experience"),
            workouts_per_week=int(request.form.get("workouts_per_week")),
        )

        db.session.add(user)
        db.session.commit()

        from flask_login import logout_user
        logout_user()


    return render_template("auth/register.html")


from flask_login import logout_user
@auth_bp.route("/logout")
def logout():
    logout_user()

    return redirect("/")


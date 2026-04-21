from flask import Blueprint, render_template, request, redirect, session
from werkzeug.security import generate_password_hash, check_password_hash
from myapp.app.extensions import db
from myapp.app.models import User

auth_bp = Blueprint("auth", __name__)


@auth_bp.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        email = request.form["email"]
        password = request.form["password"]

        user = User.query.filter_by(email=email).first()

        if not user or not check_password_hash(user.password, password):
            return "Невірний email або пароль"

        session["user"] = user.id
        return redirect("/dashboard")

    return render_template("login.html")


@auth_bp.route("/register", methods=["GET", "POST"])
def register():
    if request.method == "POST":
        name = request.form["name"]
        email = request.form["email"]
        password = request.form["password"]

        existing_user = User.query.filter_by(email=email).first()
        if existing_user:
            return "Користувач з такою поштою вже існує"

        hashed_password = generate_password_hash(password)
        new_user = User(username=name, email=email, password=hashed_password)

        db.session.add(new_user)
        db.session.commit()

        session["user"] = new_user.id
        return redirect("/dashboard")

    return render_template("register.html")


@auth_bp.route("/logout")
def logout():
    session.pop("user", None)
    return redirect("/")

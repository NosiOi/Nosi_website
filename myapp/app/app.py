from flask import Flask, render_template, request, redirect, session
from werkzeug.security import generate_password_hash, check_password_hash
from config import Config
from extensions import db

app = Flask(__name__)
app.config.from_object(Config)

db.init_app(app)

from models import User, Workout, Nutrition, Recovery


@app.route("/register", methods=["GET", "POST"])
def register():
    if request.method == "POST":
        name = request.form["name"]
        email = request.form["email"]
        password = request.form["password"]
        age = request.form["age"]
        height = request.form["height"]
        weight = request.form["weight"]
        gender = request.form["gender"]
        activity = request.form["activity"]

        # Перевірка чи існує користувач
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


@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        email = request.form["email"]
        password = request.form["password"]

        user = User.query.filter_by(email=email).first()

        if not user:
            return "Користувача не знайдено"

        if not check_password_hash(user.password, password):
            return "Невірний пароль"

        session["user"] = user.id
        return redirect("/dashboard")

    return render_template("login.html")


@app.route("/logout")
def logout():
    session.pop("user", None)
    return redirect("/")


@app.route("/account")
def account():
    if "user" not in session:
        return redirect("/login")

    user = User.query.get(session["user"])
    return render_template("account.html", user=user)


@app.route("/")
def index():
    return render_template("index.html")


@app.route("/dashboard")
def dashboard():
    if "user" not in session:
        return redirect("/login")

    return render_template("dashboard.html")


@app.route("/diet_page")
def diet():
    return render_template("diet_page.html")


@app.route("/sport")
def sport():
    return render_template("sport.html")


@app.route("/recovery")
def recovery_page():
    return render_template("recovery.html")


if __name__ == "__main__":
    app.run(debug=True)

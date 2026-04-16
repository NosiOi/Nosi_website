from flask import Flask, render_template, request, redirect, session

app = Flask(__name__)
app.secret_key = "supersecretkey"  # пізніше заміню на свій
users = {}


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

        if email in users:
            return "Користувач з такою поштою вже існує"

        users[email] = {
            "name": name,
            "password": password,
            "age": age,
            "height": height,
            "weight": weight,
            "gender": gender,
            "activity": activity,
        }

        session["user"] = email
        return redirect("/dashboard")

    return render_template("register/html")


@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        email = request.form["email"]
        password = request.form["password"]

        if email not in users:
            return "Користувача не знайдено"

        if users[email]["password"] != password:
            return "Невірний пароль"

        session["user"] = email
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

    email = session["user"]
    user = user[email]

    return render_template("account.html", user=user, user_email=email)


@app.route("/")
def index():
    return render_template("index.html")


@app.route("/dashboard")
def dashboard():
    return render_template("dashboard.html")


@app.route("/diet_page")
def diet():
    return render_template("diet_page.html")


@app.route("/sport")
def sport():
    return render_template("sport.html")


@app.route("/recovery")
def recovery():
    return render_template("recovery.html")


if __name__ == "__main__":
    app.run(debug=True)

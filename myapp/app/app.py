from flask import Flask, render_template

app = Flask(__name__)


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

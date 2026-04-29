from flask import Blueprint, render_template, request, redirect, session

questionnaire_bp = Blueprint("questionnaire", __name__, url_prefix="/questionnaire")


@questionnaire_bp.route("/", methods=["GET", "POST"])
def questionnaire():
    if request.method == "POST":
        session["environment"] = request.form.get("environment")
        session["aesthetic_focus"] = request.form.get("aesthetic_focus")
        session["performance_focus"] = request.form.get("performance_focus")
        session["weak_points"] = request.form.getlist("weak_points")
        session["strong_points"] = request.form.getlist("strong_points")

        return redirect("/plan/generate")

    return render_template("app/questionnaire.html")

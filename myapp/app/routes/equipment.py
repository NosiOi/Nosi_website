from flask import Blueprint, render_template, request, redirect, session

equipment_bp = Blueprint("equipment", __name__, url_prefix="/equipment")


@equipment_bp.route("/", methods=["GET", "POST"])
def choose_equipment():
    if request.method == "POST":
        environment = request.form.get("environment") or "gym"
        session["environment"] = environment
        return redirect("/dashboard")

    return render_template("app/equipment.html")

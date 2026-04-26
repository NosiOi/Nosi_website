from flask import Blueprint, render_template, request, redirect, url_for
from myapp.app import db
from myapp.app.models.fitness_assessment import FitnessAssessment
from myapp.app.services.training.strength_assessment import calculate_strength_index
from myapp.app.services.training.training_plan_generator import (
    generate_training_plan_for_user,
)
from flask_login import current_user, login_required

assessment_bp = Blueprint("assessment", __name__)


@assessment_bp.route("/assessment", methods=["GET", "POST"])
@login_required
def assessment():
    if request.method == "POST":
        pushups = int(request.form["pushups"])
        squats = int(request.form["squats"])
        plank = int(request.form["plank"])

        si = calculate_strength_index(pushups, squats, plank)

        assessment = FitnessAssessment(
            user_id=current_user.id,
            pushups=pushups,
            squats=squats,
            plank_seconds=plank,
            si_push=si.si_push,
            si_squat=si.si_squat,
            si_core=si.si_core,
        )

        db.session.add(assessment)
        db.session.commit()

        # Генеруємо тренувальний план
        generate_training_plan_for_user(
            user=current_user,
            assessment=assessment,
            program_type="full_body",
            location="home",
        )

        return redirect(url_for("training.training_plan"))

    return render_template("assessment.html")

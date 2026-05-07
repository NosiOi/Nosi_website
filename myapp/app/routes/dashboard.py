from flask import Blueprint, render_template, session, redirect
from myapp.app.models import User, WorkoutPlan, NutritionPlan, RecoveryPlan
from myapp.app import db
from myapp.app.services.plan_generator import PlanGenerator
from myapp.app.utils.decorators import login_required

dashboard_bp = Blueprint("dashboard", __name__)


@dashboard_bp.route("/")
def index():
    return render_template("public/landing.html")


@dashboard_bp.route("/dashboard")
@login_required
def dashboard():
    user = User.query.get(session["user"])
    return render_template("app/dashboard.html", user=user)


@dashboard_bp.route("/demo")
def demo():
    return render_template("public/demo.html")


@dashboard_bp.route("/about")
def about():
    return render_template("public/about.html")


@dashboard_bp.route("/pricing")
def pricing():
    return render_template("public/pricing.html")


@dashboard_bp.route("/sport")
@login_required
def sport_page():
    user = User.query.get(session["user"])
    return render_template("app/sport.html", user=user)


@dashboard_bp.route("/diet_page")
@login_required
def diet_page():
    user = User.query.get(session["user"])
    return render_template("app/diet_page.html", user=user)


@dashboard_bp.route("/recovery")
@login_required
def recovery_page():
    user = User.query.get(session["user"])
    return render_template("app/recovery.html", user=user)


@dashboard_bp.route("/assessment")
@login_required
def assessment_page():
    user = User.query.get(session["user"])
    return render_template("app/assessment.html", user=user)


@dashboard_bp.route("/equipment")
@login_required
def equipment_page():
    user = User.query.get(session["user"])
    return render_template("app/equipment.html", user=user)


@dashboard_bp.route("/training_plan")
@login_required
def training_plan_page():
    user = User.query.get(session["user"])
    return render_template("app/training_plan.html", user=user)


@dashboard_bp.route("/training_explanation")
@login_required
def training_explanation_page():
    user = User.query.get(session["user"])
    return render_template("app/training_explanation.html", user=user)


@dashboard_bp.route("/profile")
@login_required
def profile_page():
    user = User.query.get(session["user"])
    return render_template("app/profile.html", user=user)


@dashboard_bp.route("/questionnaire")
@login_required
def questionnaire_page():
    user = User.query.get(session["user"])
    return render_template("app/questionnaire.html", user=user)



@dashboard_bp.route("/plan")
@login_required
def plan_page():
    user = User.query.get(session["user"])

    workout = WorkoutPlan.query.filter_by(user_id=user.id).first()
    nutrition = NutritionPlan.query.filter_by(user_id=user.id).first()
    recovery = RecoveryPlan.query.filter_by(user_id=user.id).first()

    if not all([workout, nutrition, recovery]):
        return redirect("/generate_plan")

    try:
        sleep = float(recovery.plan.split("Сон: ")[1].split(" год")[0])
        water = float(recovery.plan.split("Вода: ")[1].split(" л")[0])
    except Exception:
        sleep = 8
        water = 2

    plan = {
        "sleep": sleep,
        "water": water,
        "calories": nutrition.calories,
        "protein": nutrition.protein,
        "fats": nutrition.fats,
        "carbs": nutrition.carbs,
        "training_plan": workout.plan,
    }

    return render_template("app/plan.html", plan=plan, user=user)


@dashboard_bp.route("/generate_plan")
@login_required
def generate_plan():
    user = User.query.get(session["user"])

    generator = PlanGenerator(
        age=user.age,
        sex=user.gender,
        weight=user.weight,
        height=user.height,
        activity=user.activity,
        goal=user.goal,
        experience=user.experience,
        workouts_per_week=user.workouts_per_week,
    )

    plan = generator.generate()

    workout = WorkoutPlan.query.filter_by(user_id=user.id).first() or WorkoutPlan(
        user_id=user.id
    )
    nutrition = NutritionPlan.query.filter_by(user_id=user.id).first() or NutritionPlan(
        user_id=user.id
    )
    recovery = RecoveryPlan.query.filter_by(user_id=user.id).first() or RecoveryPlan(
        user_id=user.id
    )

    workout.plan = plan["training_plan"]

    nutrition.calories = plan["calories"]
    nutrition.protein = plan["protein"]
    nutrition.fats = plan["fats"]
    nutrition.carbs = plan["carbs"]

    recovery.plan = f"Сон: {plan['sleep']} годин, Вода: {plan['water']} л"

    db.session.add_all([workout, nutrition, recovery])
    db.session.commit()

    return redirect("/plan")

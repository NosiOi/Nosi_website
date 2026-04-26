from flask import Blueprint, render_template, session, redirect
from myapp.app.models import (
    User,
    WorkoutPlan,
    NutritionPlan,
    RecoveryPlan,
)
from myapp.app import db
from myapp.app.services.plan_generator import PlanGenerator
from myapp.app.utils.decorators import login_required

dashboard_bp = Blueprint("dashboard", __name__)


@dashboard_bp.route("/")
def index():
    return render_template("landing.html")


@dashboard_bp.route("/dashboard")
@login_required
def dashboard():
    user = User.query.get(session["user"])
    return render_template("dashboard.html", user=user)


@dashboard_bp.route("/plan")
@login_required
def plan_page():
    user = User.query.get(session["user"])

    workout = WorkoutPlan.query.filter_by(user_id=user.id).first()
    nutrition = NutritionPlan.query.filter_by(user_id=user.id).first()
    recovery = RecoveryPlan.query.filter_by(user_id=user.id).first()

    if not workout or not nutrition or not recovery:
        return redirect("/generate_plan")

    sleep = float(recovery.plan.split("Сон: ")[1].split(" год")[0])
    water = float(recovery.plan.split("Вода: ")[1].split(" л")[0])

    plan = {
        "sleep": sleep,
        "water": water,
        "calories": nutrition.calories,
        "protein": nutrition.protein,
        "fats": nutrition.fats,
        "carbs": nutrition.carbs,
        "training_plan": workout.plan,
    }

    return render_template("plan.html", plan=plan, user=user)


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

    workout = WorkoutPlan.query.filter_by(user_id=user.id).first()
    nutrition = NutritionPlan.query.filter_by(user_id=user.id).first()
    recovery = RecoveryPlan.query.filter_by(user_id=user.id).first()

    if not workout:
        workout = WorkoutPlan(user_id=user.id)
    if not nutrition:
        nutrition = NutritionPlan(user_id=user.id)
    if not recovery:
        recovery = RecoveryPlan(user_id=user.id)

    workout.plan = plan["training_plan"]
    nutrition.calories = plan["calories"]
    nutrition.protein = plan["protein"]
    nutrition.fats = plan["fats"]
    nutrition.carbs = plan["carbs"]
    recovery.plan = f"Сон: {plan['sleep']} годин, Вода: {plan['water']} л"

    db.session.add(workout)
    db.session.add(nutrition)
    db.session.add(recovery)
    db.session.commit()

    return redirect("/plan")

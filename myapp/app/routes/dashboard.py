from flask import Blueprint, render_template, session, redirect, url_for
from myapp.app.models import User, WorkoutPlan, NutritionPlan, RecoveryPlan
from myapp.app.extensions import db
from myapp.app.services.plan_generator import PlanGenerator

dashboard_bp = Blueprint("dashboard", __name__)


@dashboard_bp.route("/")
def index():
    return render_template("landing.html")


@dashboard_bp.route("/dashboard")
def dashboard():
    if "user" not in session:
        return redirect("/login")

    user = User.query.get(session["user"])
    return render_template("dashboard.html", user=user)


@dashboard_bp.route("/plan")
def plan_page():
    if "user" not in session:
        return redirect("/login")

    user = User.query.get(session["user"])

    workout = WorkoutPlan.query.filter_by(user_id=user.id).first()
    nutrition = NutritionPlan.query.filter_by(user_id=user.id).first()
    recovery = RecoveryPlan.query.filter_by(user_id=user.id).first()

    if not workout or not nutrition or not recovery:
        return redirect("/generate_plan")

    return render_template(
        "plan.html", user=user, workout=workout, nutrition=nutrition, recovery=recovery
    )


@dashboard_bp.route("/generate_plan")
def generate_plan():
    if "user" not in session:
        return redirect("/login")

    user = User.query.get(session["user"])

    if (
        WorkoutPlan.query.filter_by(user_id=user.id).first()
        and NutritionPlan.query.filter_by(user_id=user.id).first()
        and RecoveryPlan.query.filter_by(user_id=user.id).first()
    ):
        return redirect("/plan")

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

    workout = WorkoutPlan(user_id=user.id, plan=plan["training_plan"])
    nutrition = NutritionPlan(
        user_id=user.id,
        calories=plan["calories"],
        protein=plan["protein"],
        fats=plan["fats"],
        carbs=plan["carbs"],
    )
    recovery = RecoveryPlan(
        user_id=user.id, plan=f"Сон: {plan['sleep']} годин, Вода: {plan['water']} л"
    )

    db.session.add(workout)
    db.session.add(nutrition)
    db.session.add(recovery)
    db.session.commit()

    return redirect("/plan")

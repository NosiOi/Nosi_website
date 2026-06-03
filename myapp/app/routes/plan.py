from flask import Blueprint, render_template, redirect
from flask_login import login_required, current_user
from myapp.app.models import User, WorkoutPlan, NutritionPlan, RecoveryPlan
from myapp.app import db
from myapp.app.services.plan_generator import PlanGenerator

plan_bp = Blueprint("plan", __name__, url_prefix="/plan")


@plan_bp.route("/view")
@login_required
def view_plan():
    user = current_user

    workout = WorkoutPlan.query.filter_by(user_id=user.id).first()
    nutrition = NutritionPlan.query.filter_by(user_id=user.id).first()
    recovery = RecoveryPlan.query.filter_by(user_id=user.id).first()

    if not all([workout, nutrition, recovery]):
        return redirect("/plan/generate")

    plan = {
        "training_plan": workout.plan,
        "calories": nutrition.calories,
        "protein": nutrition.protein,
        "fats": nutrition.fats,
        "carbs": nutrition.carbs,
        "recovery": recovery.plan,
    }

    return render_template("app/plan.html", plan=plan, user=user)


@plan_bp.route("/generate")
@login_required
def generate_plan():
    user = current_user

    generator = PlanGenerator(
        age=user.age,
        sex=user.gender,
        weight=user.weight,
        height=user.height,
        activity=user.activity,
        goal=user.goal,
        experience=user.experience,
        workouts_per_week=user.workouts_per_week,
        environment=user.environment if hasattr(user, "environment") else "gym",
        aesthetic_focus=user.aesthetic_focus if hasattr(user, "aesthetic_focus") else None,
        performance_focus=user.performance_focus if hasattr(user, "performance_focus") else None,
        weak_points=user.weak_points if hasattr(user, "weak_points") else [],
        strong_points=user.strong_points if hasattr(user, "strong_points") else [],
    )

    plan = generator.generate()

    workout = WorkoutPlan.query.filter_by(user_id=user.id).first() or WorkoutPlan(user_id=user.id)
    nutrition = NutritionPlan.query.filter_by(user_id=user.id).first() or NutritionPlan(user_id=user.id)
    recovery = RecoveryPlan.query.filter_by(user_id=user.id).first() or RecoveryPlan(user_id=user.id)

    workout.plan = plan["training_plan"]
    nutrition.calories = plan["calories"]
    nutrition.protein = plan["protein"]
    nutrition.fats = plan["fats"]
    nutrition.carbs = plan["carbs"]
    recovery.plan = f"Сон: {plan['sleep']} годин, Вода: {plan['water']} л"

    db.session.add_all([workout, nutrition, recovery])
    db.session.commit()

    return redirect("/plan/view")

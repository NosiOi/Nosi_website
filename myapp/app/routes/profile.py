from flask import Blueprint, render_template, session, redirect, request
from myapp.app.models import User, WorkoutPlan, NutritionPlan, RecoveryPlan
from myapp.app import db
from myapp.app.services.plan_generator import PlanGenerator
from myapp.app.utils.decorators import login_required

profile_bp = Blueprint("profile", __name__)


@profile_bp.route("/profile")
@login_required
def profile():
    user = User.query.get(session["user"])
    return render_template("profile.html", user=user)


@profile_bp.route("/profile/edit", methods=["GET", "POST"])
@login_required
def edit_profile():
    user = User.query.get(session["user"])

    if request.method == "POST":
        # 1. Оновлюємо дані користувача
        user.username = request.form["username"]
        user.email = request.form["email"]
        user.age = int(request.form["age"])
        user.height = float(request.form["height"])
        user.weight = float(request.form["weight"])
        user.gender = request.form["gender"]
        user.activity = float(request.form["activity"])
        user.goal = request.form["goal"]
        user.experience = request.form["experience"]
        user.workouts_per_week = int(request.form["workouts_per_week"])

        db.session.commit()

        # 2. Генеруємо новий план
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

        # 3. Оновлюємо або створюємо плани
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

        # 4. Повертаємо користувача в профіль
        return redirect("/profile")

    return render_template("profile_edit.html", user=user)

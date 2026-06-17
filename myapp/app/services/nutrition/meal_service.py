from datetime import date, datetime

from myapp.app import db
from myapp.app.models import Meal


def recalc_meal_totals(meal: Meal):
    meal.total_calories = sum(i.calories for i in meal.items)
    meal.total_protein = sum(i.protein for i in meal.items)
    meal.total_fat = sum(i.fat for i in meal.items)
    meal.total_carbs = sum(i.carbs for i in meal.items)


def add_meal_service(user_id, form):
    meal = Meal(
        user_id=user_id,
        date=date.today(),
        time=form.get("time"),
        name=form["name"],
        category=form["category"],
        total_calories=int(form.get("kcal", 0)),
        total_protein=int(form.get("protein", 0)),
        total_fat=int(form.get("fat", 0)),
        total_carbs=int(form.get("carb", 0)),
    )

    db.session.add(meal)
    db.session.commit()


def delete_meal_service(user_id, meal_id):
    meal = Meal.query.filter_by(id=meal_id, user_id=user_id).first()
    if meal:
        db.session.delete(meal)
        db.session.commit()


def copy_meal_service(user_id, meal_id):
    from myapp.app.models import MealItem

    source = Meal.query.filter_by(id=meal_id, user_id=user_id).first()
    if not source:
        return

    new_meal = Meal(
        user_id=user_id,
        date=date.today(),
        time=datetime.now().time(),
        total_calories=0,
        total_protein=0,
        total_fat=0,
        total_carbs=0,
        name=source.name,
        category=source.category,
    )

    db.session.add(new_meal)
    db.session.flush()

    for item in source.items:
        db.session.add(
            MealItem(
                meal_id=new_meal.id,
                name=item.name,
                calories=item.calories,
                protein=item.protein,
                fat=item.fat,
                carbs=item.carbs,
            )
        )

    db.session.flush()

    recalc_meal_totals(new_meal)

    db.session.commit()

from myapp.app import db
from myapp.app.models import Meal, MealItem, User
from myapp.app.services.nutrition.meal_service import recalc_meal_totals


def add_item_service(user_id, form):
    user = User.query.get(user_id)

    meal_id = int(form["meal_id"])
    meal = Meal.query.filter_by(id=meal_id, user_id=user_id).first()
    if not meal:
        return

    item = MealItem(
        meal_id=meal.id,
        name=form["name"],
        calories=int(form.get("calories", 0)),
        protein=int(form.get("protein", 0)),
        fat=int(form.get("fat", 0)),
        carbs=int(form.get("carbs", 0)),
        fiber=0,
        category_label=None
    )

    db.session.add(item)
    db.session.flush()

    recalc_meal_totals(meal)

    db.session.add(meal)
    db.session.commit()


def delete_item_service(user_id, item_id):
    item = (
        MealItem.query.join(Meal)
        .filter(MealItem.id == item_id, Meal.user_id == user_id)
        .first()
    )
    if not item:
        return

    meal = item.meal

    db.session.delete(item)
    db.session.flush()

    recalc_meal_totals(meal)

    db.session.add(meal)
    db.session.commit()

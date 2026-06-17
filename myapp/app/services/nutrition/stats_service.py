from datetime import date, timedelta

from myapp.app.models import Meal, UserWeight
from myapp.app.services.nutrition.day_service import get_goals


def get_stats(user_id, days=7):
    today = date.today()

    labels = []
    kcal_values = []

    for i in range(days):
        d = today - timedelta(days=i)
        meals = Meal.query.filter_by(user_id=user_id, date=d).all()
        labels.append(d.strftime("%d.%m"))
        kcal_values.append(sum(m.total_calories for m in meals))

    labels.reverse()
    kcal_values.reverse()

    weights = (
        UserWeight.query.filter_by(user_id=user_id)
        .order_by(UserWeight.date.asc())
        .all()
    )

    weight_labels = [w.date.strftime("%d.%m") for w in weights]
    weight_values = [w.weight for w in weights]

    goal_cal, _, _, _ = get_goals(user_id)

    avg_kcal = sum(kcal_values) // len(kcal_values) if kcal_values else 0

    return {
        "kcal": {
            "labels": labels,
            "values": kcal_values
        },
        "weight": {
            "labels": weight_labels,
            "values": weight_values
        },
        "avg_kcal": avg_kcal,
        "goal_kcal": goal_cal,
        "current_weight": weight_values[-1] if weight_values else None,
        "weight_trend": "Стабільно"
    }

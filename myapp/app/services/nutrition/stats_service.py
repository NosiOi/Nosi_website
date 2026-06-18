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


def get_year_heatmap(user_id, year: int):
    start = date(year, 1, 1)
    end = date(year, 12, 31)

    goal_cal, _, _, _ = get_goals(user_id)

    days = []
    d = start
    while d <= end:
        meals = Meal.query.filter_by(user_id=user_id, date=d).all()
        kcal = sum(m.total_calories for m in meals)

        if goal_cal > 0:
            percent = round((kcal / goal_cal) * 100)
        else:
            percent = 0

        if percent == 0:
            level = 0
        elif percent <= 25:
            level = 1
        elif percent <= 50:
            level = 2
        elif percent <= 75:
            level = 3
        else:
            level = 4

        days.append(
            {
                "date": d.isoformat(),
                "kcal": kcal,
                "percent": percent,
                "level": level,
            }
        )

        d += timedelta(days=1)

    return {
        "year": year,
        "days": days,
    }
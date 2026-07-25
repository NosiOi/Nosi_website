import os
import json

from myapp.app import create_app, db
from myapp.app.models.recovery.habit import RecoveryHabit

BASE_DIR = os.path.abspath(
    os.path.join(
        os.path.dirname(__file__),
        "data",
        "habits",
    )
)

FILE_PATH = os.path.join(BASE_DIR, "habits.json")


def run():
    app = create_app()
    with app.app_context():
        with open(FILE_PATH, "r", encoding="utf-8") as f:
            habits = json.load(f)

        for h in habits:
            slug = h.get("slug")
            if not slug:
                continue

            habit = RecoveryHabit.query.filter_by(slug=slug).first()
            if habit is None:
                habit = RecoveryHabit(slug=slug)
                db.session.add(habit)

            habit.name = h.get("name", slug)
            habit.description = h.get("description")
            habit.category = h.get("category")
            habit.points = h.get("points", 0)
            habit.icon = h.get("icon")
            habit.daily_log_limit = h.get("daily_log_limit", 1)
            habit.estimated_minutes = h.get("estimated_minutes", 0)
            habit.recommended_when = h.get("recommended_when", [])
            habit.premium_only = h.get("premium_only", False)
            habit.sort_order = h.get("sort_order", 0)
            habit.is_active = True
            habit.is_archived = False

        db.session.commit()
        print("Habits seeded successfully.")


if __name__ == "__main__":
    run()

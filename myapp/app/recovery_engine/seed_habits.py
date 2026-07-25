import os
import json
from myapp.app import create_app, db
from myapp.app.models.recovery.habit import RecoveryHabit

BASE_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), "data", "habits"))

FILE_PATH = os.path.join(BASE_DIR, "habits.json")


def run():
    app = create_app()
    with app.app_context():
        with open(FILE_PATH, "r", encoding="utf-8") as f:
            habits = json.load(f)

        for h in habits:
            if RecoveryHabit.query.filter_by(slug=h["slug"]).first():
                continue

            habit = RecoveryHabit(
                slug=h["slug"],
                name=h["name"],
                description=h.get("description"),
                category=h.get("category"),
                points=h.get("points", 0),
                icon=h.get("icon"),
                daily_limit=h.get("daily_limit", 1),
                estimated_minutes=h.get("estimated_minutes", 0),
                recommended_when=h.get("recommended_when", []),
                premium_only=h.get("premium_only", False),
                sort_order=h.get("sort_order", 0),
                is_active=True,
            )

            db.session.add(habit)

        db.session.commit()
        print("Habits seeded successfully.")


if __name__ == "__main__":
    run()

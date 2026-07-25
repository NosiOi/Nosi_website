import json
from myapp.app import create_app, db
from myapp.app.models.recovery.habit import Habit


def run():
    app = create_app()
    with app.app_context():
        path = "myapp/app/recovery_engine/data/habits.json"
        with open(path, "r", encoding="utf-8") as f:
            habits = json.load(f)

        for h in habits:
            if Habit.query.filter_by(slug=h["slug"]).first():
                continue

            habit = Habit(
                slug=h["slug"],
                name=h["name"],
                description=h.get("description"),
                category=h.get("category"),
                score=h.get("score", 0),
                icon=h.get("icon"),
                recommended_when=h.get("recommended_when", []),
                is_active=True,
            )
            db.session.add(habit)

        db.session.commit()
        print("Habits seeded successfully.")


if __name__ == "__main__":
    run()

from myapp.app import db
from myapp.app.models import Exercise

EXERCISES = [
    {
        "name": "Жим лежачи",
        "muscle_group": "chest",
        "equipment": "gym",
        "difficulty": "intermediate",
    },
    {
        "name": "Віджимання",
        "muscle_group": "chest",
        "equipment": "home",
        "difficulty": "beginner",
    },
    {
        "name": "Підтягування",
        "muscle_group": "back",
        "equipment": "outdoor",
        "difficulty": "intermediate",
    },
]


def seed_exercises():
    for ex in EXERCISES:
        if not Exercise.query.filter_by(name=ex["name"]).first():
            db.session.add(
                Exercise(
                    name=ex["name"],
                    muscle_group=ex["muscle_group"],
                    equipment=ex["equipment"],
                    difficulty=ex["difficulty"],
                )
            )
    db.session.commit()


if __name__ == "__main__":
    from myapp.app import create_app

    app = create_app()
    with app.app_context():
        seed_exercises()

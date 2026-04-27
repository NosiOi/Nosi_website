from myapp.app import create_app, db
from myapp.app.models.equipment import Equipment
from myapp.app.models.exercise import Exercise


def seed_equipment():
    equipment_items = [
        ("bodyweight", "Власна вага"),
        ("dumbbells", "Гантелі"),
        ("kettlebells", "Гирі"),
        ("pullup_bar", "Турнік"),
        ("gym_machines", "Тренажери"),
    ]

    for name, display in equipment_items:
        if not Equipment.query.filter_by(name=name).first():
            db.session.add(Equipment(name=name, display_name=display))

    db.session.commit()
    print("✔ Обладнання додано")


def seed_exercises():
    exercises_data = [
        # PUSH
        ("Віджимання від підлоги", "push", "push", 0.2, 0.0, 0.0, ["bodyweight"]),
        (
            "Віджимання з вузькою постановкою рук",
            "push",
            "push",
            0.4,
            0.2,
            0.1,
            ["bodyweight"],
        ),
        ("Жим гантелей лежачи", "push", "push", 0.5, 0.3, 0.2, ["dumbbells"]),
        ("Жим гантелей сидячи", "push", "push", 0.6, 0.4, 0.3, ["dumbbells"]),
        ("Жим на тренажері", "push", "push", 0.7, 0.5, 0.3, ["gym_machines"]),
        # LEGS
        ("Присідання", "legs", "legs", 0.2, 0.0, 0.0, ["bodyweight"]),
        ("Випади вперед", "legs", "legs", 0.3, 0.1, 0.0, ["bodyweight"]),
        ("Болгарські присідання", "legs", "legs", 0.5, 0.3, 0.2, ["bodyweight"]),
        ("Присідання з гантелями", "legs", "legs", 0.6, 0.4, 0.3, ["dumbbells"]),
        ("Жим ногами", "legs", "legs", 0.7, 0.5, 0.3, ["gym_machines"]),
        # CORE
        ("Скручування", "core", "core", 0.1, 0.0, 0.0, ["bodyweight"]),
        ("Планка", "core", "core", 0.2, 0.0, 0.0, ["bodyweight"]),
        ("Підйом ніг у висі", "core", "core", 0.6, 0.4, 0.3, ["pullup_bar"]),
        ("Russian Twist", "core", "core", 0.4, 0.2, 0.1, ["bodyweight"]),
        ("Скручування з гантеллю", "core", "core", 0.5, 0.3, 0.2, ["dumbbells"]),
        # FULL BODY
        ("Бурпі", "full", None, 0.5, 0.3, 0.2, ["bodyweight"]),
        ("Махи гирею", "full", None, 0.6, 0.4, 0.3, ["kettlebells"]),
        ("Тяга гантелі в нахилі", "full", None, 0.5, 0.3, 0.2, ["dumbbells"]),
        ("Тяга верхнього блока", "full", None, 0.6, 0.4, 0.3, ["gym_machines"]),
    ]

    for name, mg, stype, diff, min_si, min_exp, eq_list in exercises_data:
        if Exercise.query.filter_by(name=name).first():
            continue

        ex = Exercise(
            name=name,
            muscle_group=mg,
            strength_type=stype,
            difficulty=diff,
            min_strength_index=min_si,
            min_experience=min_exp,
        )

        for eq_name in eq_list:
            eq = Equipment.query.filter_by(name=eq_name).first()
            if eq:
                ex.equipment.append(eq)

        db.session.add(ex)

    db.session.commit()
    print("✔ Вправи додано")


if __name__ == "__main__":
    app = create_app()
    with app.app_context():
        seed_equipment()
        seed_exercises()
        print("🎉 Seed завершено успішно!")

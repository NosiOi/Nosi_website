import json
import os
import sys

from myapp.app import create_app, db


def get_default_data_path():
    return os.path.abspath(
        os.path.join(
            os.path.dirname(__file__),
            "..",
            "app",
            "training_engine",
            "data",
            "exercises",
            "base_exercises.json",
        )
    )


def run_seed(data_path=None):
    app = create_app()

    if data_path is None:
        data_path = get_default_data_path()

    if not os.path.exists(data_path):
        raise FileNotFoundError(f"Seed file not found: {data_path}")

    with app.app_context():
        from myapp.app.training_engine.models.exercise import Exercise
        from myapp.app.training_engine.models.muscle import Muscle
        from myapp.app.training_engine.models.equipment import TEEquipment

        def get_or_create_muscle(slug, name=None):
            m = Muscle.query.filter_by(slug=slug).first()
            if not m:
                m = Muscle(slug=slug, name=name or slug.capitalize())
                db.session.add(m)
                db.session.flush()
            return m

        def get_or_create_equipment(name):
            e = TEEquipment.query.filter_by(name=name).first()
            if not e:
                e = TEEquipment(name=name)
                db.session.add(e)
                db.session.flush()
            return e

        with open(data_path, "r", encoding="utf-8") as f:
            items = json.load(f)

        for it in items:
            slug = it.get("slug") or it["name"].lower().replace(" ", "-")
            ex = Exercise.query.filter_by(slug=slug).first()
            if ex:
                continue

            ex = Exercise(
                name=it["name"],
                slug=slug,
                description=it.get("description"),
                difficulty=it.get("difficulty", 1),
                location=it.get("location", "any"),
                movement_pattern=it.get("movement_pattern"),
                risk_level=it.get("risk_level", 1),
                progression=json.dumps(it.get("progression", [])),
                regression=json.dumps(it.get("regression", [])),
            )
            db.session.add(ex)
            db.session.flush()

            # append muscles to association table (no load_percent required)
            for mslug in it.get("muscles_primary", []) + it.get("muscles_secondary", []):
                m = get_or_create_muscle(mslug, mslug.capitalize())
                if m not in ex.muscles:
                    ex.muscles.append(m)

            for ename in it.get("equipment", []):
                e = get_or_create_equipment(ename)
                ex.equipment.append(e)

        db.session.commit()
        print("Seed complete.")


if __name__ == "__main__":
    arg = sys.argv[1] if len(sys.argv) > 1 else None
    run_seed(arg)

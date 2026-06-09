import json
import os
from myapp.app import create_app, db
from myapp.app.training_engine.models.exercise import Exercise
from myapp.app.training_engine.models.muscle import Muscle
from myapp.app.training_engine.models.equipment import TEEquipment

APP = create_app()
DATA_PATH = os.path.join(os.path.dirname(__file__), "..", "data", "exercises_seed.json")


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


with APP.app_context():
    with open(DATA_PATH, "r", encoding="utf-8") as f:
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
            regression=json.dumps(it.get("regression", []))
        )
        db.session.add(ex)
        db.session.flush()
        for mslug in it.get("muscles_primary", []) + it.get("muscles_secondary", []):
            m = get_or_create_muscle(mslug, mslug.capitalize())
            ex.muscles.append(m)
        for ename in it.get("equipment", []):
            e = get_or_create_equipment(ename)
            ex.equipment.append(e)
    db.session.commit()
    print("Seed complete.")

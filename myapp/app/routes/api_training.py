from flask import Blueprint, jsonify, request, current_app
from flask_login import login_required, current_user
from myapp.app import db
from myapp.app.training_engine.models.exercise import Exercise
from myapp.app.training_engine.models.muscle import Muscle
from myapp.app.training_engine.models.equipment import TEEquipment
from myapp.app.training_engine.models.training_plan import TrainingPlan
from myapp.app.training_engine.models.session import Session
from myapp.app.training_engine.models.user_pref import UserPreference
from sqlalchemy import func
import json

bp = Blueprint("api_training", __name__, url_prefix="/api")


@bp.route("/muscles", methods=["GET"])
@login_required
def list_muscles():
    items = Muscle.query.order_by(Muscle.name).all()
    return jsonify([m.to_dict() for m in items])


@bp.route("/equipment", methods=["GET"])
@login_required
def list_equipment():
    items = TEEquipment.query.order_by(TEEquipment.name).all()
    return jsonify([e.to_dict() for e in items])


@bp.route("/exercises", methods=["GET"])
@login_required
def list_exercises():
    q = Exercise.query
    muscle = request.args.get("muscle")
    location = request.args.get("location")
    qstr = request.args.get("q")
    if muscle:
        q = q.join(Exercise.muscles).filter(func.lower(Muscle.slug) == muscle.lower())
    if location and location != "any":
        q = q.filter(Exercise.location == location)
    if qstr:
        q = q.filter(Exercise.name.ilike(f"%{qstr}%"))
    items = q.limit(500).all()
    return jsonify([ex.to_dict() for ex in items])


@bp.route("/exercises/<int:exercise_id>", methods=["GET"])
@login_required
def get_exercise(exercise_id):
    ex = Exercise.query.get_or_404(exercise_id)
    return jsonify(ex.to_dict())


@bp.route("/training/today", methods=["GET"])
@login_required
def training_today():
    plan = TrainingPlan.query.filter_by(user_id=current_user.id, is_active=True).first()
    prefs = {p.key: p.value for p in UserPreference.query.filter_by(user_id=current_user.id).all()}
    avoid_muscles = [k.split("injury_")[1] for k, v in prefs.items() if k.startswith("injury_") and v == "true"]
    no_equipment = prefs.get("no_equipment", "")
    no_equipment_list = [s.strip().lower() for s in (no_equipment or "").split(",") if s.strip()]

    session_payload = {"sessionId": None, "title": None, "exercises": [], "muscles": {}, "plan": []}

    if plan:
        session_payload["sessionId"] = f"plan-{plan.id}"
        session_payload["title"] = plan.name
        session_payload["plan"] = [{"id": plan.id, "name": plan.name}]
        try:
            meta = json.loads(plan.meta or "{}")
        except Exception:
            meta = {}
        ex_ids = []
        days = meta.get("days", {})
        if isinstance(days, dict):
            for day in days.values():
                for ex in day.get("exercises", []):
                    if isinstance(ex, int):
                        ex_ids.append(ex)
                    elif isinstance(ex, dict) and ex.get("id"):
                        ex_ids.append(ex.get("id"))
        elif isinstance(days, list):
            for day in days:
                for ex in day.get("exercises", []):
                    if isinstance(ex, int):
                        ex_ids.append(ex)
                    elif isinstance(ex, dict) and ex.get("id"):
                        ex_ids.append(ex.get("id"))
        if ex_ids:
            ex_objs = Exercise.query.filter(Exercise.id.in_(ex_ids)).all()
        else:
            ex_objs = Exercise.query.limit(6).all()
    else:
        session_payload["sessionId"] = "fallback"
        session_payload["title"] = "Рекомендована сесія"
        ex_objs = Exercise.query.order_by(Exercise.difficulty.asc()).limit(6).all()

    filtered = []
    for ex in ex_objs:
        muscle_slugs = [m.slug.lower() for m in ex.muscles]
        if any(ms in avoid_muscles for ms in muscle_slugs):
            continue
        if no_equipment_list:
            eq_names = [e.name.lower() for e in ex.equipment]
            if any(ne in eq_names for ne in no_equipment_list):
                continue
        filtered.append(ex)

    muscles_count = {}
    for ex in filtered:
        for m in ex.muscles:
            muscles_count[m.slug] = muscles_count.get(m.slug, 0) + 1
    total = sum(muscles_count.values()) or 1
    muscles_pct = {k: round(v / total, 3) for k, v in muscles_count.items()}

    session_payload["exercises"] = [ex.to_dict() for ex in filtered]
    session_payload["muscles"] = muscles_pct
    return jsonify(session_payload)


@bp.route("/session/<int:session_id>", methods=["GET"])
@login_required
def get_session(session_id):
    s = Session.query.get_or_404(session_id)
    return jsonify(s.to_dict())


@bp.route("/plans", methods=["POST"])
@login_required
def create_plan():
    data = request.get_json() or {}
    name = data.get("name", "Мій план")
    meta = data.get("meta", "{}")
    plan = TrainingPlan(user_id=current_user.id, name=name, meta=meta)
    db.session.add(plan)
    db.session.commit()
    return jsonify({"id": plan.id, "name": plan.name}), 201


@bp.route("/user/preferences", methods=["GET", "POST"])
@login_required
def user_preferences():
    if request.method == "GET":
        prefs = UserPreference.query.filter_by(user_id=current_user.id).all()
        return jsonify({p.key: p.value for p in prefs})
    data = request.get_json() or {}
    for k, v in data.items():
        pref = UserPreference.query.filter_by(user_id=current_user.id, key=k).first()
        if pref:
            pref.value = v
        else:
            pref = UserPreference(user_id=current_user.id, key=k, value=v)
            db.session.add(pref)
    db.session.commit()
    return jsonify({"status": "ok"})

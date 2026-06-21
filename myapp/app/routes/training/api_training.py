from flask import Blueprint, jsonify, request, current_app
from flask_login import login_required, current_user
from myapp.app import db
from myapp.app.training_engine.models.exercise import Exercise
from myapp.app.training_engine.models.muscle import Muscle
from myapp.app.training_engine.models.equipment import TEEquipment
from myapp.app.training_engine.models.training_plan import TrainingPlan
from myapp.app.training_engine.models.session import Session
from myapp.app.training_engine.models.user_pref import UserPreference
from myapp.app.services.training_engine_service import TrainingEngineService
from sqlalchemy import func
import datetime as dt
import json

bp = Blueprint("api", __name__, url_prefix="/api")


def _error_response(e):
    current_app.logger.exception("API error")
    try:
        msg = str(e)
    except Exception:
        msg = "internal error"
    return jsonify({"error": "internal_server_error", "message": msg}), 500


@bp.route("/muscles", methods=["GET"])
@login_required
def list_muscles():
    try:
        items = Muscle.query.order_by(Muscle.name).all()
        return jsonify([m.to_dict() for m in items])
    except Exception as e:
        return _error_response(e)


@bp.route("/equipment", methods=["GET"])
@login_required
def list_equipment():
    try:
        items = TEEquipment.query.order_by(TEEquipment.name).all()
        return jsonify([e.to_dict() for e in items])
    except Exception as e:
        return _error_response(e)


@bp.route("/exercises", methods=["GET"])
@login_required
def list_exercises():
    try:
        q = Exercise.query
        muscle = request.args.get("muscle")
        equipment = request.args.get("equipment")
        qstr = request.args.get("q")
        page = int(request.args.get("page", 1))
        per_page = int(request.args.get("per_page", 50))

        if muscle:
            q = q.join(Exercise.muscles).filter(func.lower(Muscle.slug) == muscle.lower())
        if equipment:
            q = q.join(Exercise.equipment).filter(func.lower(TEEquipment.name) == equipment.lower())
        if qstr:
            q = q.filter(Exercise.name.ilike(f"%{qstr}%"))

        items = q.order_by(Exercise.name).paginate(page=page, per_page=per_page, error_out=False)
        return jsonify({
            "items": [ex.to_dict() for ex in items.items],
            "page": page,
            "per_page": per_page,
            "total": items.total
        })
    except Exception as e:
        return _error_response(e)


@bp.route("/exercises/<int:exercise_id>", methods=["GET"])
@login_required
def get_exercise(exercise_id):
    try:
        ex = Exercise.query.get_or_404(exercise_id)
        return jsonify(ex.to_dict())
    except Exception as e:
        return _error_response(e)


@bp.route("/training/today", methods=["GET"])
@login_required
def training_today():
    try:
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
            try:
                muscle_slugs = [m.slug.lower() for m in ex.muscles]
            except Exception:
                muscle_slugs = []
            if any(ms in avoid_muscles for ms in muscle_slugs):
                continue
            if no_equipment_list:
                try:
                    eq_names = [e.name.lower() for e in ex.equipment]
                except Exception:
                    eq_names = []
                if any(ne in eq_names for ne in no_equipment_list):
                    continue
            filtered.append(ex)

        muscles_count = {}
        for ex in filtered:
            if hasattr(ex, "exercise_muscles") and ex.exercise_muscles:
                for em in ex.exercise_muscles:
                    if hasattr(em, "muscle"):
                        mslug = getattr(em.muscle, "slug", None)
                        if not mslug:
                            continue
                        load = getattr(em, "load_percent", None)
                        if load is None:
                            load = 60 if getattr(em, "is_primary", False) else 20
                        muscles_count[mslug] = muscles_count.get(mslug, 0) + (load or 0)
            else:
                try:
                    muscles = ex.muscles or []
                except Exception:
                    muscles = []
                if not muscles:
                    continue
                per = 100.0 / len(muscles)
                for m in muscles:
                    mslug = getattr(m, "slug", None)
                    if not mslug:
                        continue
                    muscles_count[mslug] = muscles_count.get(mslug, 0) + per

        total = sum(muscles_count.values()) or 1
        muscles_pct = {k: round(v / total, 3) for k, v in muscles_count.items()}

        session_payload["exercises"] = [ex.to_dict() for ex in filtered]
        session_payload["muscles"] = muscles_pct
        return jsonify(session_payload)
    except Exception as e:
        return _error_response(e)


@bp.route("/session", methods=["POST"])
@login_required
def create_session():
    try:
        data = request.get_json() or {}
        plan_id = data.get("plan_id")
        title = data.get("title") or (f"Сесія плану {plan_id}" if plan_id else "Нова сесія")
        session = Session(user_id=current_user.id, plan_id=plan_id, title=title, data=data.get("data"))
        db.session.add(session)
        db.session.commit()
        return jsonify(session.to_dict()), 201
    except Exception as e:
        return _error_response(e)


@bp.route("/session/<int:session_id>/exercises", methods=["POST"])
@login_required
def add_exercise_to_session(session_id):
    try:
        s = Session.query.filter_by(id=session_id, user_id=current_user.id).first_or_404()
        payload = request.get_json() or {}
        ex_id = payload.get("exercise_id")
        sets = payload.get("sets", 3)
        reps = payload.get("reps", "8")
        try:
            data = json.loads(s.data) if s.data else {"exercises": []}
        except Exception:
            data = {"exercises": []}
        data.setdefault("exercises", []).append({
            "id": ex_id,
            "sets": sets,
            "reps": reps,
            "added_at": dt.datetime.utcnow().isoformat()
        })
        s.data = json.dumps(data)
        db.session.add(s)
        db.session.commit()
        return jsonify(s.to_dict())
    except Exception as e:
        return _error_response(e)


@bp.route("/session/<int:session_id>", methods=["PATCH"])
@login_required
def patch_session(session_id):
    try:
        s = Session.query.filter_by(id=session_id, user_id=current_user.id).first_or_404()
        payload = request.get_json() or {}
        if "data" in payload:
            newdata = payload.get("data")
            if isinstance(newdata, dict):
                s.data = json.dumps(newdata)
            else:
                s.data = newdata
        if "title" in payload:
            s.title = payload.get("title")
        db.session.add(s)
        db.session.commit()
        return jsonify(s.to_dict())
    except Exception as e:
        return _error_response(e)


@bp.route("/session/<int:session_id>/finish", methods=["POST"])
@login_required
def finish_session(session_id):
    try:
        s = Session.query.filter_by(id=session_id, user_id=current_user.id).first_or_404()
        s.finished_at = dt.datetime.utcnow()
        db.session.add(s)
        db.session.commit()
        return jsonify(s.to_dict())
    except Exception as e:
        return _error_response(e)


@bp.route("/reports/muscle-load", methods=["GET"])
@login_required
def report_muscle_load():
    try:
        from_ts = request.args.get("from")
        to_ts = request.args.get("to")
        try:
            if from_ts:
                from_dt = dt.datetime.fromisoformat(from_ts)
            else:
                from_dt = dt.datetime.utcnow() - dt.timedelta(days=7)
            if to_ts:
                to_dt = dt.datetime.fromisoformat(to_ts)
            else:
                to_dt = dt.datetime.utcnow()
        except Exception:
            from_dt = dt.datetime.utcnow() - dt.timedelta(days=7)
            to_dt = dt.datetime.utcnow()

        sessions = Session.query.filter(
            Session.user_id == current_user.id,
            Session.created_at >= from_dt,
            Session.created_at <= to_dt
        ).all()

        session_payloads = []
        for s in sessions:
            try:
                payload = json.loads(s.data) if s.data else {}
            except Exception:
                payload = {}
            session_payloads.append(payload)

        def exercise_lookup(ex_id):
            try:
                return Exercise.query.get(int(ex_id))
            except Exception:
                return None

        return jsonify({"sessions": len(session_payloads)})
    except Exception as e:
        return _error_response(e)


@bp.route("/training/heatmap", methods=["GET"])
@login_required
def training_heatmap():
    try:
        year = int(request.args.get("year", dt.date.today().year))
        start = dt.date(year, 1, 1)
        end = dt.date(year, 12, 31)

        sessions = Session.query.filter(
            Session.user_id == current_user.id,
            Session.created_at >= dt.datetime.combine(start, dt.time.min),
            Session.created_at <= dt.datetime.combine(end, dt.time.max)
        ).all()

        loads = {}
        for s in sessions:
            day = s.created_at.date()
            try:
                payload = json.loads(s.data) if s.data else {}
            except Exception:
                payload = {}
            exs = payload.get("exercises", [])
            load_value = len(exs) * 20
            loads[day] = loads.get(day, 0) + load_value

        days = []
        d = start
        today = dt.date.today()
        while d <= end:
            load = loads.get(d, 0)
            if load == 0:
                level = 0
            elif load < 30:
                level = 1
            elif load < 60:
                level = 2
            elif load < 90:
                level = 3
            else:
                level = 4

            days.append({
                "date": d.strftime("%Y-%m-%d"),
                "load": load,
                "level": level,
                "is_today": (d == today)
            })

            d += dt.timedelta(days=1)

        return jsonify({"days": days})
    except Exception as e:
        return _error_response(e)


@bp.route("/training/plan", methods=["GET"])
@login_required
def get_plan():
    week = int(request.args.get("week", 1))
    try:
        plan = TrainingEngineService.generate_plan(current_user, week)
        return jsonify(plan.to_dict())
    except Exception as e:
        current_app.logger.exception("Error generating training plan")
        return jsonify({"error": "failed to generate plan", "message": str(e)}), 500


@bp.route("/training/plan_mock", methods=["GET"])
def get_plan_mock():
    sample = {
        "id": "mock-1",
        "name": "Тестовий план",
        "type": "adaptive",
        "duration": 45,
        "meta": {
            "days": [
                {
                    "day_name": "day1",
                    "exercises": [
                        {"exercise_id": "ex-fixt-1", "name": "Жим лежачи", "sets": [{"target": 80}], "reps": "8-10"},
                        {"exercise_id": "ex-fixt-2", "name": "Підтягування", "sets": [{"target": 0}], "reps": "6-8"}
                    ]
                }
            ],
            "radar": {"Chest": 0.8, "Back": 0.6, "Legs": 0.7},
            "balance_hints": ["Фокус на великих групах", "Додати 1 день відновлення"]
        }
    }
    return jsonify(sample)


@bp.route("/training/analytics", methods=["GET"])
@login_required
def get_analytics():
    try:
        performance = getattr(current_user, "performance_state", None)
        recovery = getattr(current_user, "fatigue_state", None)
        analytics = TrainingEngineService.compute_analytics(performance, recovery)
        return jsonify(analytics)
    except Exception as e:
        current_app.logger.exception("Error computing analytics")
        return jsonify({"error": "failed to compute analytics", "message": str(e)}), 500


@bp.route("/training/recommendations", methods=["GET"])
@login_required
def get_recommendations():
    try:
        from myapp.app.training_engine.recommendations.weak_point_analysis import WeakPointAnalysis
        from myapp.app.training_engine.recommendations.exercise_recommendations import ExerciseRecommendations
        from myapp.app.training_engine.recommendations.recovery_recommendations import RecoveryRecommendations
        from myapp.app.training_engine.recommendations.nutrition_recommendations import NutritionRecommendations

        profile = TrainingEngineService.build_profile(current_user)

        weak = WeakPointAnalysis.analyze(profile.weak_points, profile.strong_points)
        ex = ExerciseRecommendations.for_weak_points(profile.weak_points, profile.environment)
        rec = RecoveryRecommendations.generate(
            sleep=getattr(current_user.fatigue_state, "sleep", None),
            stress=getattr(current_user.fatigue_state, "stress", None),
            soreness=getattr(current_user.fatigue_state, "soreness", None),
            hydration=getattr(current_user.fatigue_state, "hydration", None)
        )
        nut = NutritionRecommendations.generate(profile.goal)

        return jsonify({
            "weak_points": weak,
            "exercise_recommendations": ex,
            "recovery": rec,
            "nutrition": nut
        })
    except Exception as e:
        current_app.logger.exception("Error generating recommendations")
        return jsonify({"error": "failed to generate recommendations", "message": str(e)}), 500

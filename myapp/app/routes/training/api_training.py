from flask import Blueprint, jsonify, request, current_app
from flask_login import login_required, current_user
from myapp.app import db
from myapp.app.training_engine.models.exercise import Exercise
from myapp.app.training_engine.models.muscle import Muscle
from myapp.app.training_engine.models.equipment import TEEquipment
from myapp.app.training_engine.models.training_plan import TrainingPlan
from myapp.app.training_engine.models.user_pref import UserPreference
from myapp.app.services.training_engine_service import TrainingEngineService
from myapp.app.services.training_session_service import TrainingSessionService
from myapp.app.models.training_session import TrainingSession, SessionExercise
from sqlalchemy import func
import datetime as dt
import json

bp = Blueprint("api_training", __name__, url_prefix="/api/training")


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


@bp.route("/exercises/<exercise_id>", methods=["GET"])
@login_required
def get_exercise(exercise_id):
    try:
        ex = Exercise.query.get_or_404(exercise_id)
        return jsonify(ex.to_dict())
    except Exception as e:
        return _error_response(e)


@bp.route("/today", methods=["GET"])
@login_required
def training_today():
    try:
        active = TrainingSession.query.filter_by(
            user_id=current_user.id,
            status="active"
        ).order_by(TrainingSession.started_at.desc()).first()

        prefs = {p.key: p.value for p in UserPreference.query.filter_by(user_id=current_user.id).all()}
        avoid_muscles = [k.split("injury_")[1] for k, v in prefs.items() if k.startswith("injury_") and v == "true"]
        no_equipment = prefs.get("no_equipment", "")
        no_equipment_list = [s.strip().lower() for s in (no_equipment or "").split(",") if s.strip()]

        payload = {"sessionId": None, "title": None, "exercises": [], "muscles": {}, "plan": [], "hints": []}

        if active:
            payload["sessionId"] = str(active.id)
            payload["title"] = "Активна сесія"
            ex_objs = []
            for se in active.exercises:
                ex = Exercise.query.get(se.exercise_id)
                if not ex:
                    continue
                ex_objs.append(ex)
        else:
            plan = TrainingPlan.query.filter_by(user_id=current_user.id, is_active=True).first()
            payload["sessionId"] = None
            payload["title"] = "Рекомендована сесія"
            payload["plan"] = []
            if plan:
                payload["plan"] = [{"id": plan.id, "name": plan.name}]
                try:
                    meta = json.loads(plan.meta or "{}")
                except Exception:
                    meta = {}
                ex_ids = []
                days = meta.get("days", {})
                if isinstance(days, dict):
                    for day in days.values():
                        for ex in day.get("exercises", []):
                            if isinstance(ex, str):
                                ex_ids.append(ex)
                            elif isinstance(ex, dict) and ex.get("id"):
                                ex_ids.append(str(ex.get("id")))
                elif isinstance(days, list):
                    for day in days:
                        for ex in day.get("exercises", []):
                            if isinstance(ex, str):
                                ex_ids.append(ex)
                            elif isinstance(ex, dict) and ex.get("id"):
                                ex_ids.append(str(ex.get("id")))
                if ex_ids:
                    ex_objs = Exercise.query.filter(Exercise.id.in_(ex_ids)).all()
                else:
                    ex_objs = Exercise.query.limit(6).all()
            else:
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

        payload["exercises"] = [ex.to_dict() for ex in filtered]
        payload["muscles"] = muscles_pct
        payload["hints"] = []

        return jsonify(payload)
    except Exception as e:
        return _error_response(e)


@bp.route("/heatmap", methods=["GET"])
@login_required
def training_heatmap():
    try:
        year = int(request.args.get("year", dt.date.today().year))
        start = dt.date(year, 1, 1)
        end = dt.date(year, 12, 31)

        sessions = TrainingSession.query.filter(
            TrainingSession.user_id == current_user.id,
            TrainingSession.started_at >= dt.datetime.combine(start, dt.time.min),
            TrainingSession.started_at <= dt.datetime.combine(end, dt.time.max)
        ).all()

        loads = {}
        for s in sessions:
            day = s.started_at.date()
            total_load = 0
            for se in s.exercises:
                sets = se.sets_done or se.sets_planned or 0
                try:
                    reps_val = se.reps_done or se.reps_planned or "0"
                    reps = int(str(reps_val).split("-")[0])
                except Exception:
                    reps = 0
                load = (se.load_done or se.load_planned or 0) * sets * max(reps, 1)
                total_load += load
            loads[day] = loads.get(day, 0) + total_load

        days = []
        d = start
        today = dt.date.today()
        while d <= end:
            load = loads.get(d, 0)
            if load == 0:
                level = 0
            elif load < 1000:
                level = 1
            elif load < 3000:
                level = 2
            elif load < 6000:
                level = 3
            else:
                level = 4

            days.append({
                "date": d.strftime("%Y-%m-%d"),
                "load": int(load),
                "level": level,
                "is_today": (d == today)
            })

            d += dt.timedelta(days=1)

        return jsonify({"days": days})
    except Exception as e:
        return _error_response(e)


@bp.route("/plan", methods=["GET"])
@login_required
def get_plan():
    week = int(request.args.get("week", 1))
    try:
        plan = TrainingEngineService.generate_plan(current_user, week)
        return jsonify(plan.to_dict())
    except Exception as e:
        current_app.logger.exception("Error generating training plan")
        return jsonify({"error": "failed to generate plan", "message": str(e)}), 500


@bp.route("/analytics", methods=["GET"])
@login_required
def get_analytics():
    try:
        performance = getattr(current_user, "performance_state", None)
        recovery = getattr(current_user, "fatigue_state", None)
        analytics = TrainingEngineService.compute_analytics(performance, recovery)
        return jsonify({
            "performance": analytics["strength"],
            "recovery": analytics["recovery"],
            "strength": analytics["strength"],
            "endurance": analytics["endurance"],
            "mobility": analytics["mobility"],
            "fatigue": analytics["fatigue"],
        })
    except Exception as e:
        current_app.logger.exception("Error computing analytics")
        return jsonify({"error": "failed to compute analytics", "message": str(e)}), 500


@bp.route("/recommendations", methods=["GET"])
@login_required
def get_recommendations():
    try:
        from myapp.app.training_engine.recommendations.weak_point_analysis import WeakPointAnalysis
        from myapp.app.training_engine.recommendations.exercise_recommendations import ExerciseRecommendations
        from myapp.app.training_engine.recommendations.recovery_recommendations import RecoveryRecommendations
        from myapp.app.training_engine.recommendations.nutrition_recommendations import NutritionRecommendations

        profile = TrainingEngineService.build_profile(current_user)

        weak = WeakPointAnalysis.analyze(profile.weak_points or [], profile.strong_points or [])

        env = getattr(profile, "environment", "gym")
        ex = ExerciseRecommendations.for_weak_points(profile.weak_points or [], env)

        fs = getattr(current_user, "fatigue_state", None)
        sleep = getattr(fs, "sleep", 7) if fs else 7
        stress = getattr(fs, "stress", 0) if fs else 0
        soreness = getattr(fs, "soreness", 0) if fs else 0
        hydration = getattr(fs, "hydration", 2.0) if fs else 2.0

        rec = RecoveryRecommendations.generate(
            sleep=sleep,
            stress=stress,
            soreness=soreness,
            hydration=hydration
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


@bp.route("/session/start", methods=["POST"])
@login_required
def start_session():
    try:
        data = request.get_json() or {}
        fatigue_before = data.get("fatigue_before")
        session = TrainingSessionService.start_session(current_user, fatigue_before=fatigue_before)
        return jsonify({"id": session.id})
    except Exception as e:
        return _error_response(e)


@bp.route("/session/<int:session_id>/exercise/<exercise_id>", methods=["POST"])
@login_required
def update_session_exercise(session_id, exercise_id):
    try:
        data = request.get_json() or {}
        session = TrainingSession.query.filter_by(id=session_id, user_id=current_user.id).first_or_404()
        se = TrainingSessionService.update_exercise(session, exercise_id, data)
        return jsonify({"exercise_id": se.exercise_id})
    except Exception as e:
        return _error_response(e)


@bp.route("/session/<int:session_id>/finish", methods=["POST"])
@login_required
def finish_session(session_id):
    try:
        data = request.get_json() or {}
        fatigue_after = data.get("fatigue_after")
        session = TrainingSession.query.filter_by(id=session_id, user_id=current_user.id).first_or_404()
        TrainingSessionService.finish_session(session, fatigue_after=fatigue_after)
        return jsonify({"status": "ok"})
    except Exception as e:
        return _error_response(e)


@bp.route("/strength-test", methods=["POST"])
@login_required
def strength_test():
    data = request.json or {}

    pushups = data.get("pushups", 0)
    squats = data.get("squats", 0)
    situps = data.get("situps", 0)

    if not current_user.performance_state:
        from myapp.app.training_engine.models.performance_state import PerformanceState
        ps = PerformanceState(
            pushups=pushups,
            squats=squats,
            situps=situps,
            weight=current_user.weight
        )
        db.session.add(ps)
        db.session.flush()
        current_user.performance_state_id = ps.id
    else:
        ps = current_user.performance_state
        ps.pushups = pushups
        ps.squats = squats
        ps.situps = situps

    db.session.commit()

    return jsonify({"status": "ok"})

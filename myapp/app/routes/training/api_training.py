from flask import Blueprint, jsonify, request, current_app
from flask_login import login_required, current_user
from myapp.app import db
from myapp.app.training_engine.models.exercise import Exercise
from myapp.app.training_engine.models.muscle import Muscle
from myapp.app.training_engine.models.equipment import TEEquipment
from myapp.app.training_engine.models.user_pref import UserPreference
from myapp.app.services.training_engine_service import TrainingEngineService
from myapp.app.services.training_session_service import TrainingSessionService
from myapp.app.models.training_session import TrainingSession, SessionExercise
from myapp.app.training_engine.models.training_plan import TrainingPlan
from myapp.app.training_engine.models.performance_state import PerformanceState
from sqlalchemy import func
import datetime as dt

bp = Blueprint("api_training", __name__, url_prefix="/api/training")


def _error_response(e):
    current_app.logger.exception("API error")
    return jsonify({"error": "internal_server_error", "message": str(e)}), 500


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
            q = q.join(Exercise.muscles).filter(
                func.lower(Muscle.slug) == muscle.lower()
            )
        if equipment:
            q = q.join(Exercise.equipment).filter(
                func.lower(TEEquipment.name) == equipment.lower()
            )
        if qstr:
            q = q.filter(Exercise.name.ilike(f"%{qstr}%"))

        items = q.order_by(Exercise.name).paginate(
            page=page, per_page=per_page, error_out=False
        )

        return jsonify(
            {
                "items": [ex.to_dict() for ex in items.items],
                "page": page,
                "per_page": per_page,
                "total": items.total,
            }
        )
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


def _get_active_plan_for_user(user):
    plan = (
        TrainingPlan.query.filter_by(user_id=user.id, is_active=True)
        .order_by(TrainingPlan.id.desc())
        .first()
    )
    if not plan:
        plan = TrainingEngineService.generate_plan(user)
    return plan


def _get_day_key_for_today():
    mapping = {
        0: "mon",
        1: "tue",
        2: "wed",
        3: "thu",
        4: "fri",
        5: "sat",
        6: "sun",
    }
    return mapping[dt.date.today().weekday()]


@bp.route("/today", methods=["GET"])
@login_required
def training_today():
    try:
        active = (
            TrainingSession.query.filter_by(user_id=current_user.id, status="active")
            .order_by(TrainingSession.started_at.desc())
            .first()
        )

        prefs = {
            p.key: p.value
            for p in UserPreference.query.filter_by(user_id=current_user.id).all()
        }
        avoid_muscles = [
            k.split("injury_")[1]
            for k, v in prefs.items()
            if k.startswith("injury_") and v == "true"
        ]
        no_equipment_list = [
            s.strip().lower()
            for s in (prefs.get("no_equipment") or "").split(",")
            if s.strip()
        ]

        payload = {
            "sessionId": None,
            "title": None,
            "exercises": [],
            "muscles": {},
            "plan": [],
            "hints": [],
        }

        if active:
            payload["sessionId"] = str(active.id)
            payload["title"] = "Активна сесія"
            ex_objs = [
                Exercise.query.get(se.exercise_id)
                for se in active.exercises
                if Exercise.query.get(se.exercise_id)
            ]
        else:
            plan = _get_active_plan_for_user(current_user)
            day_key = _get_day_key_for_today()
            day = plan.days.get(day_key) or next(iter(plan.days.values()))
            ex_objs = []

            for ex in day.get("exercises", []):
                if isinstance(ex, dict) and "exercise_id" in ex:
                    ex_obj = Exercise.query.get(ex["exercise_id"])
                    if ex_obj:
                        ex_objs.append(ex_obj)
                elif isinstance(ex, Exercise):
                    ex_objs.append(ex)

            payload["title"] = "Рекомендована сесія"
            payload["plan"] = [{"id": getattr(plan, "id", 0), "name": plan.name}]

        filtered = []
        for ex in ex_objs:
            muscles = getattr(ex, "muscles", [])
            if any(m.slug.lower() in avoid_muscles for m in muscles):
                continue
            if no_equipment_list:
                eq_names = [e.name.lower() for e in getattr(ex, "equipment", [])]
                if any(ne in eq_names for ne in no_equipment_list):
                    continue
            filtered.append(ex)

        muscles_count = {}
        for ex in filtered:
            muscles = getattr(ex, "muscles", [])
            if not muscles:
                continue
            per = 100.0 / len(muscles)
            for m in muscles:
                muscles_count[m.slug] = muscles_count.get(m.slug, 0) + per

        total = sum(muscles_count.values()) or 1
        muscles_pct = {k: round(v / total, 3) for k, v in muscles_count.items()}

        payload["exercises"] = [
            ex if isinstance(ex, dict) else ex.to_dict() for ex in filtered
        ]
        payload["muscles"] = muscles_pct

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
            TrainingSession.started_at <= dt.datetime.combine(end, dt.time.max),
        ).all()

        loads = {}
        for s in sessions:
            day = s.started_at.date()
            total_load = 0
            for se in s.exercises:
                sets = se.sets_done or se.sets_planned or 0
                reps = int(str(se.reps_done or se.reps_planned or "0").split("-")[0])
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

            days.append(
                {
                    "date": d.strftime("%Y-%m-%d"),
                    "load": int(load),
                    "level": level,
                    "is_today": (d == today),
                }
            )

            d += dt.timedelta(days=1)

        return jsonify({"days": days})

    except Exception as e:
        return _error_response(e)


@bp.route("/plan", methods=["GET"])
@login_required
def get_plan():
    try:
        plan = _get_active_plan_for_user(current_user)
        return jsonify(plan.to_dict())
    except Exception as e:
        return _error_response(e)


@bp.route("/analytics", methods=["GET"])
@login_required
def get_analytics():
    try:
        perf = current_user.performance_state
        rec = current_user.fatigue_state

        performance = {
            "pushups": getattr(perf, "pushups", 0),
            "squats": getattr(perf, "squats", 0),
            "situps": getattr(perf, "situps", 0),
            "plank_sec": getattr(perf, "plank_sec", 0),
            "weight": getattr(current_user, "weight", 70),
            "training_load": getattr(perf, "training_load", 0),
            "hip": getattr(perf, "hip", 0),
            "shoulder": getattr(perf, "shoulder", 0),
            "thoracic": getattr(perf, "thoracic", 0),
            "ankle": getattr(perf, "ankle", 0),
        }

        recovery = {
            "sleep": getattr(rec, "sleep", 7),
            "stress": getattr(rec, "stress", 0),
            "soreness": getattr(rec, "soreness", 0),
            "hydration": getattr(rec, "hydration", 2.0),
        }

        result = TrainingEngineService.compute_analytics(performance, recovery)
        return jsonify(result)

    except Exception as e:
        return _error_response(e)


@bp.route("/recommendations", methods=["GET"])
@login_required
def get_recommendations():
    try:
        from myapp.app.training_engine.recommendations.weak_point_analysis import (
            WeakPointAnalysis,
        )
        from myapp.app.training_engine.recommendations.exercise_recommendations import (
            ExerciseRecommendations,
        )
        from myapp.app.training_engine.recommendations.recovery_recommendations import (
            RecoveryRecommendations,
        )
        from myapp.app.training_engine.recommendations.nutrition_recommendations import (
            NutritionRecommendations,
        )

        profile = TrainingEngineService.build_profile(current_user)

        weak = WeakPointAnalysis.analyze(profile.weak_points, profile.strong_points)
        ex = ExerciseRecommendations.for_weak_points(
            profile.weak_points, profile.environment
        )

        fs = getattr(current_user, "fatigue_state", None)
        sleep = getattr(fs, "sleep", 7) if fs else 7
        stress = getattr(fs, "stress", 0) if fs else 0
        soreness = getattr(fs, "soreness", 0) if fs else 0
        hydration = getattr(fs, "hydration", 2.0) if fs else 2.0

        rec = RecoveryRecommendations.generate(sleep, stress, soreness, hydration)
        nut = NutritionRecommendations.generate(profile.goal)

        return jsonify(
            {
                "weak_points": weak,
                "exercise_recommendations": ex,
                "recovery": rec,
                "nutrition": nut,
            }
        )

    except Exception as e:
        return _error_response(e)


@bp.route("/session/start", methods=["POST"])
@login_required
def start_session():
    try:
        data = request.get_json() or {}
        fatigue_before = data.get("fatigue_before")
        session = TrainingSessionService.start_session(current_user, fatigue_before)
        return jsonify({"id": session.id})
    except Exception as e:
        return _error_response(e)


@bp.route("/session/<int:session_id>/exercise/<exercise_id>", methods=["POST"])
@login_required
def update_session_exercise(session_id, exercise_id):
    try:
        data = request.get_json() or {}
        session = TrainingSession.query.filter_by(
            id=session_id, user_id=current_user.id
        ).first_or_404()
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
        session = TrainingSession.query.filter_by(
            id=session_id, user_id=current_user.id
        ).first_or_404()
        TrainingSessionService.finish_session(session, fatigue_after)
        return jsonify({"status": "ok"})
    except Exception as e:
        return _error_response(e)


@bp.route("/strength-test", methods=["POST"])
@login_required
def strength_test():
    try:
        data = request.json or {}

        pushups = data.get("pushups", 0)
        squats = data.get("squats", 0)
        situps = data.get("situps", 0)
        plank_sec = data.get("plank_sec", 0)

        if not current_user.performance_state:
            ps = PerformanceState(
                pushups=pushups,
                squats=squats,
                situps=situps,
                plank_sec=plank_sec,
                weight=current_user.weight,
            )
            db.session.add(ps)
            db.session.flush()
            current_user.performance_state_id = ps.id
        else:
            ps = current_user.performance_state
            ps.pushups = pushups
            ps.squats = squats
            ps.situps = situps
            ps.plank_sec = plank_sec

        db.session.commit()
        return jsonify({"status": "ok"})

    except Exception as e:
        return _error_response(e)


@bp.route("/plans", methods=["GET"])
@login_required
def list_plans():
    try:
        plans = TrainingPlan.query.filter_by(user_id=current_user.id).all()
        return jsonify([p.to_dict() for p in plans])
    except Exception as e:
        return _error_response(e)


@bp.route("/plans", methods=["POST"])
@login_required
def create_plan():
    try:
        data = request.get_json() or {}
        name = data.get("name", "Plan")
        days_data_raw = data.get("days", {})
        is_active = data.get("is_active", False)

        plan = TrainingPlan(user_id=current_user.id, name=name, is_active=is_active)

        days_struct = {}
        for key, items in days_data_raw.items():
            days_struct[key] = {
                "exercises": [
                    {
                        "exercise_id": ex["exercise_id"],
                        "sets": ex.get("sets"),
                        "reps": ex.get("reps"),
                        "load": ex.get("load"),
                    }
                    for ex in items
                ]
            }

        plan.days = days_struct

        if is_active:
            TrainingPlan.query.filter_by(
                user_id=current_user.id, is_active=True
            ).update({"is_active": False})

        db.session.add(plan)
        db.session.commit()
        return jsonify(plan.to_dict())
    except Exception as e:
        return _error_response(e)


@bp.route("/plans/<int:plan_id>", methods=["GET"])
@login_required
def get_plan_by_id(plan_id):
    try:
        plan = TrainingPlan.query.filter_by(
            id=plan_id, user_id=current_user.id
        ).first_or_404()
        return jsonify(plan.to_dict())
    except Exception as e:
        return _error_response(e)


@bp.route("/plans/<int:plan_id>", methods=["PUT"])
@login_required
def update_plan(plan_id):
    try:
        plan = TrainingPlan.query.filter_by(
            id=plan_id, user_id=current_user.id
        ).first_or_404()

        data = request.get_json() or {}
        plan.name = data.get("name", plan.name)
        is_active = data.get("is_active", plan.is_active)

        days_data_raw = data.get("days", {})
        days_struct = {}
        for key, items in days_data_raw.items():
            days_struct[key] = {
                "exercises": [
                    {
                        "exercise_id": ex["exercise_id"],
                        "sets": ex.get("sets"),
                        "reps": ex.get("reps"),
                        "load": ex.get("load"),
                    }
                    for ex in items
                ]
            }

        plan.days = days_struct

        if is_active:
            TrainingPlan.query.filter_by(
                user_id=current_user.id, is_active=True
            ).update({"is_active": False})
            plan.is_active = True
        else:
            plan.is_active = False

        db.session.commit()
        return jsonify(plan.to_dict())
    except Exception as e:
        return _error_response(e)


@bp.route("/plans/<int:plan_id>", methods=["DELETE"])
@login_required
def delete_plan(plan_id):
    try:
        plan = TrainingPlan.query.filter_by(
            id=plan_id, user_id=current_user.id
        ).first_or_404()
        db.session.delete(plan)
        db.session.commit()
        return jsonify({"status": "ok"})
    except Exception as e:
        return _error_response(e)


@bp.route("/sessions/complete", methods=["POST"])
@login_required
def complete_session():
    try:
        data = request.get_json() or {}

        raw = data.get("exercises", [])
        exercises = []

        if isinstance(raw, dict):
            for day_items in raw.values():
                if isinstance(day_items, list):
                    exercises.extend(day_items)
        elif isinstance(raw, list):
            exercises = raw

        session = TrainingSession(
            user_id=current_user.id,
            started_at=dt.datetime.utcnow(),
            status="finished",
        )
        db.session.add(session)
        db.session.flush()

        for ex in exercises:
            se = SessionExercise(
                session_id=session.id,
                exercise_id=ex["exercise_id"],
                sets_done=ex.get("sets") or ex.get("sets_done"),
                reps_done=ex.get("reps") or ex.get("reps_done"),
                load_done=ex.get("load") or ex.get("load_done"),
            )
            db.session.add(se)

        db.session.commit()
        TrainingSessionService.update_training_load_from_session(session, current_user)
        return jsonify({"id": session.id})
    except Exception as e:
        return _error_response(e)

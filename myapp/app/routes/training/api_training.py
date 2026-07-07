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


def _error(e):
    current_app.logger.exception("API error")
    return jsonify({"error": "internal_server_error", "message": str(e)}), 500


def _active_plan(user):
    plan = (
        TrainingPlan.query.filter_by(user_id=user.id, is_active=True)
        .order_by(TrainingPlan.id.desc())
        .first()
    )
    return plan or TrainingEngineService.generate_plan(user)


def _today_key():
    return ["mon", "tue", "wed", "thu", "fri", "sat", "sun"][dt.date.today().weekday()]


def _plan_days_struct(raw):
    result = {}
    for key, items in raw.items():
        day_ex = []
        for ex in items:
            ex_id = ex["exercise"]["id"]
            obj = Exercise.query.get(ex_id)
            day_ex.append(
                {
                    "exercise": {"id": obj.id, "name": obj.name},
                    "sets": ex.get("sets") or 3,
                    "reps": ex.get("reps") or "8-12",
                    "load": ex.get("load") or 0,
                }
            )
        result[key] = {"exercises": day_ex}
    return result


def _session_load(session):
    return TrainingSessionService._compute_session_load(session)


@bp.route("/muscles")
@login_required
def muscles():
    try:
        return jsonify([m.to_dict() for m in Muscle.query.order_by(Muscle.name)])
    except Exception as e:
        return _error(e)


@bp.route("/equipment")
@login_required
def equipment():
    try:
        return jsonify(
            [e.to_dict() for e in TEEquipment.query.order_by(TEEquipment.name)]
        )
    except Exception as e:
        return _error(e)


@bp.route("/exercises")
@login_required
def exercises():
    try:
        q = Exercise.query
        muscle = request.args.get("muscle")
        equipment = request.args.get("equipment")
        qstr = request.args.get("q")
        page = int(request.args.get("page", 1))
        per_page = int(request.args.get("per_page", 50))

        if muscle:
            q = q.filter(
                Exercise.muscles_primary.contains([muscle])
                | Exercise.muscles_secondary.contains([muscle])
            )

        if equipment:
            q = q.filter(Exercise.equipment.contains([equipment]))

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
        return _error(e)


@bp.route("/today")
@login_required
def today():
    try:
        active = (
            TrainingSession.query.filter_by(user_id=current_user.id, status="active")
            .order_by(TrainingSession.started_at.desc())
            .first()
        )

        prefs = {
            p.key: p.value
            for p in UserPreference.query.filter_by(user_id=current_user.id)
        }
        avoid = [
            k.split("injury_")[1]
            for k, v in prefs.items()
            if k.startswith("injury_") and v == "true"
        ]
        no_eq = [
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
        }

        exercises_raw = []

        if active:
            payload["sessionId"] = str(active.id)
            payload["title"] = "Активна сесія"
            for se in active.exercises:
                ex_obj = Exercise.query.filter_by(id=se.exercise_id).first()
                if not ex_obj:
                    continue
                exercises_raw.append(
                    {
                        "exercise": ex_obj,
                        "sets": se.sets_done or se.sets_planned or 0,
                        "reps": se.reps_done or se.reps_planned or "8-12",
                        "load": se.load_done or se.load_planned or 0,
                    }
                )
        else:
            plan = _active_plan(current_user)
            day = plan.days.get(_today_key()) or next(iter(plan.days.values()))
            for ex in day["exercises"]:
                ex_id = ex["exercise"]["id"]
                ex_obj = Exercise.query.get(ex_id)
                if not ex_obj:
                    continue
                exercises_raw.append(
                    {
                        "exercise": ex_obj,
                        "sets": ex.get("sets") or 3,
                        "reps": ex.get("reps") or "8-12",
                        "load": ex.get("load") or 0,
                    }
                )

            payload["title"] = "Рекомендована сесія"
            payload["plan"] = [{"id": plan.id, "name": plan.name}]

        filtered = []
        for item in exercises_raw:
            ex = item["exercise"]
            if any(m.slug.lower() in avoid for m in ex.muscles):
                continue
            if no_eq and any(e.name.lower() in no_eq for e in ex.equipment):
                continue
            filtered.append(item)

        muscles = {}
        for item in filtered:
            ex = item["exercise"]
            per = 100 / len(ex.muscles) if ex.muscles else 0
            for m in ex.muscles:
                muscles[m.slug] = muscles.get(m.slug, 0) + per

        total = sum(muscles.values()) or 1
        payload["muscles"] = {k: round(v / total, 3) for k, v in muscles.items()}
        payload["exercises"] = [
            {
                "name": item["exercise"].name,
                "sets": item["sets"],
                "reps": item["reps"],
                "load": item["load"],
            }
            for item in filtered
        ]

        return jsonify(payload)
    except Exception as e:
        return _error(e)


@bp.route("/today-session")
@login_required
def today_session():
    try:
        active = (
            TrainingSession.query.filter_by(user_id=current_user.id, status="active")
            .order_by(TrainingSession.started_at.desc())
            .first()
        )

        result = {"exercises": []}

        if active:
            for se in active.exercises:
                ex = Exercise.query.get(se.exercise_id)
                if not ex:
                    continue
                result["exercises"].append(
                    {
                        "name": ex.name,
                        "sets": se.sets_done or se.sets_planned or 0,
                        "reps": se.reps_done or se.reps_planned or "8-12",
                        "load": se.load_done or se.load_planned or 0,
                    }
                )
            return jsonify(result)

        plan = _active_plan(current_user)
        day = plan.days.get(_today_key()) or next(iter(plan.days.values()))

        for item in day["exercises"]:
            ex_id = item["exercise"]["id"]
            ex = Exercise.query.get(ex_id)
            if not ex:
                continue
            result["exercises"].append(
                {
                    "name": ex.name,
                    "sets": item.get("sets") or 3,
                    "reps": item.get("reps") or "8-12",
                    "load": item.get("load") or 0,
                }
            )

        return jsonify(result)
    except Exception as e:
        return _error(e)


@bp.route("/heatmap")
@login_required
def heatmap():
    try:
        year = int(request.args.get("year", dt.date.today().year))
        start = dt.date(year, 1, 1)
        end = dt.date(year, 12, 31)

        sessions = TrainingSession.query.filter(
            TrainingSession.user_id == current_user.id,
            TrainingSession.started_at >= dt.datetime.combine(start, dt.time.min),
            TrainingSession.started_at <= dt.datetime.combine(end, dt.time.max),
        )

        loads = {}
        for s in sessions:
            day = s.started_at.date()
            loads[day] = loads.get(day, 0) + _session_load(s)

        perf = current_user.performance_state
        pushups = getattr(perf, "pushups", 0) if perf else 0
        squats = getattr(perf, "squats", 0) if perf else 0
        situps = getattr(perf, "situps", 0) if perf else 0
        user_level = (
            (pushups + squats + situps) / 3 if (pushups or squats or situps) else 0
        )

        if user_level < 10:
            user_mult = 1.4
        elif user_level < 30:
            user_mult = 1.0
        else:
            user_mult = 0.7

        max_load = max(loads.values()) if loads else 0

        days = []
        d = start
        today = dt.date.today()

        while d <= end:
            load = loads.get(d, 0)
            percent = min(100, int((load / max_load) * 100)) if max_load > 0 else 0

            if percent == 0:
                level = 0
            elif percent < 20:
                level = 1
            elif percent < 40:
                level = 2
            elif percent < 70:
                level = 3
            else:
                level = 4

            days.append(
                {
                    "date": d.strftime("%Y-%m-%d"),
                    "load": int(load),
                    "percent": percent,
                    "level": level,
                    "is_today": d == today,
                }
            )
            d += dt.timedelta(days=1)

        return jsonify({"days": days})
    except Exception as e:
        return _error(e)


@bp.route("/plans", methods=["GET"])
@login_required
def plans():
    try:
        return jsonify(
            [p.to_dict() for p in TrainingPlan.query.filter_by(user_id=current_user.id)]
        )
    except Exception as e:
        return _error(e)


@bp.route("/plans", methods=["POST"])
@login_required
def create_plan():
    try:
        data = request.get_json() or {}
        plan = TrainingPlan(
            user_id=current_user.id,
            name=data.get("name", "Plan"),
            is_active=data.get("is_active", False),
            days=_plan_days_struct(data.get("days", {})),
        )

        if plan.is_active:
            TrainingPlan.query.filter_by(
                user_id=current_user.id, is_active=True
            ).update({"is_active": False})

        db.session.add(plan)
        db.session.commit()
        return jsonify(plan.to_dict())
    except Exception as e:
        return _error(e)


@bp.route("/plans/<int:plan_id>", methods=["PUT"])
@login_required
def update_plan(plan_id):
    try:
        plan = TrainingPlan.query.filter_by(
            id=plan_id, user_id=current_user.id
        ).first_or_404()
        data = request.get_json() or {}

        plan.name = data.get("name", plan.name)
        plan.days = _plan_days_struct(data.get("days", {}))

        if data.get("is_active", plan.is_active):
            TrainingPlan.query.filter_by(
                user_id=current_user.id, is_active=True
            ).update({"is_active": False})
            plan.is_active = True
        else:
            plan.is_active = False

        db.session.commit()
        return jsonify(plan.to_dict())
    except Exception as e:
        return _error(e)


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
        return _error(e)


@bp.route("/sessions/complete", methods=["POST"])
@login_required
def complete_session():
    try:
        existing = TrainingSession.query.filter_by(
            user_id=current_user.id, status="active"
        ).first()

        if existing:
            existing.status = "finished"
            existing.finished_at = dt.datetime.utcnow()
            db.session.commit()

        data = request.get_json() or {}
        raw = data.get("exercises", [])
        exercises = (
            raw if isinstance(raw, list) else [i for v in raw.values() for i in v]
        )

        session = TrainingSession(
            user_id=current_user.id,
            started_at=dt.datetime.utcnow(),
            status="finished",
        )
        db.session.add(session)
        db.session.flush()

        for ex in exercises:
            db.session.add(
                SessionExercise(
                    session_id=session.id,
                    exercise_id=ex["exercise"]["id"],
                    sets_done=ex.get("sets"),
                    reps_done=ex.get("reps"),
                    load_done=ex.get("load"),
                )
            )

        db.session.commit()
        TrainingSessionService.update_training_load_from_session(session, current_user)
        return jsonify({"id": session.id})
    except Exception as e:
        return _error(e)


@bp.route("/sessions/<int:session_id>/exercise/<exercise_id>", methods=["POST"])
@login_required
def update_session_exercise(session_id, exercise_id):
    try:
        data = request.get_json() or {}

        session = TrainingSession.query.filter_by(
            id=session_id, user_id=current_user.id, status="active"
        ).first_or_404()

        se = TrainingSessionService.update_exercise(session, exercise_id, data)

        return jsonify(
            {
                "status": "ok",
                "exercise_id": exercise_id,
                "sets_done": se.sets_done,
                "reps_done": se.reps_done,
                "load_done": se.load_done,
                "rpe": se.rpe,
            }
        )
    except Exception as e:
        return _error(e)


@bp.route("/sessions/start", methods=["POST"])
@login_required
def start_session():
    try:
        data = request.get_json() or {}
        fatigue_before = data.get("fatigue_before")

        existing = (
            TrainingSession.query.filter_by(user_id=current_user.id, status="active")
            .order_by(TrainingSession.started_at.desc())
            .first()
        )
        if existing:
            return jsonify({"id": existing.id})

        session = TrainingSessionService.start_session(
            current_user,
            fatigue_before=fatigue_before,
        )

        return jsonify({"id": session.id})
    except Exception as e:
        return _error(e)


@bp.route("/sessions/<int:session_id>/finish", methods=["POST"])
@login_required
def finish_session(session_id):
    try:
        data = request.get_json() or {}
        fatigue_after = data.get("fatigue_after")

        session = TrainingSession.query.filter_by(
            id=session_id, user_id=current_user.id, status="active"
        ).first_or_404()

        TrainingSessionService.finish_session(session, fatigue_after)

        return jsonify({"status": "ok", "id": session.id})
    except Exception as e:
        return _error(e)


@bp.route("/day/<date>")
@login_required
def day_details(date):
    try:
        target = dt.datetime.strptime(date, "%Y-%m-%d").date()

        sessions = TrainingSession.query.filter(
            TrainingSession.user_id == current_user.id,
            TrainingSession.started_at >= dt.datetime.combine(target, dt.time.min),
            TrainingSession.started_at <= dt.datetime.combine(target, dt.time.max),
        )

        result = []
        for s in sessions:
            exercises = []
            for ex in s.exercises:
                obj = Exercise.query.get(ex.exercise_id)
                if obj:
                    exercises.append(
                        {
                            "name": obj.name,
                            "sets": ex.sets_done or ex.sets_planned,
                            "reps": ex.reps_done or ex.reps_planned,
                            "load": ex.load_done or ex.load_planned,
                            "rpe": ex.rpe,
                        }
                    )

            result.append(
                {
                    "session_id": s.id,
                    "fatigue_before": s.fatigue_before,
                    "fatigue_after": s.fatigue_after,
                    "exercises": exercises,
                }
            )

        return jsonify({"sessions": result})
    except Exception as e:
        return _error(e)


@bp.route("/analytics")
@login_required
def analytics():
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

        result["raw_performance"] = {
            "pushups": performance["pushups"],
            "squats": performance["squats"],
            "situps": performance["situps"],
        }

        return jsonify(result)

    except Exception as e:
        return _error(e)


@bp.route("/recommendations")
@login_required
def recommendations():
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
        return _error(e)


@bp.route("/strength-test", methods=["POST"])
@login_required
def strength_test():
    try:
        data = request.get_json() or {}

        pushups = int(data.get("pushups", 0))
        squats = int(data.get("squats", 0))
        situps = int(data.get("situps", 0))

        perf = current_user.performance_state

        if not perf:
            perf = PerformanceState(user_id=current_user.id)
            db.session.add(perf)

        perf.pushups = pushups
        perf.squats = squats
        perf.situps = situps

        db.session.commit()

        return jsonify(
            {
                "status": "ok",
                "raw_performance": {
                    "pushups": pushups,
                    "squats": squats,
                    "situps": situps,
                },
            }
        )

    except Exception as e:
        return _error(e)

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
    return {
        key: {
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
        for key, items in raw.items()
    }


def _session_load(session):
    total = 0
    for se in session.exercises:
        sets = se.sets_done or se.sets_planned or 0
        reps = int(str(se.reps_done or se.reps_planned or "0").split("-")[0])
        load = (se.load_done or se.load_planned or 0) * sets * max(reps, 1)
        total += load
    return total


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

        if active:
            payload["sessionId"] = str(active.id)
            payload["title"] = "Активна сесія"
            ex_objs = [Exercise.query.get(se.exercise_id) for se in active.exercises]
        else:
            plan = _active_plan(current_user)
            day = plan.days.get(_today_key()) or next(iter(plan.days.values()))
            ex_objs = [Exercise.query.get(ex["exercise_id"]) for ex in day["exercises"]]
            payload["title"] = "Рекомендована сесія"
            payload["plan"] = [{"id": plan.id, "name": plan.name}]

        filtered = []
        for ex in ex_objs:
            if not ex:
                continue
            if any(m.slug.lower() in avoid for m in ex.muscles):
                continue
            if no_eq and any(e.name.lower() in no_eq for e in ex.equipment):
                continue
            filtered.append(ex)

        muscles = {}
        for ex in filtered:
            per = 100 / len(ex.muscles) if ex.muscles else 0
            for m in ex.muscles:
                muscles[m.slug] = muscles.get(m.slug, 0) + per

        total = sum(muscles.values()) or 1
        payload["muscles"] = {k: round(v / total, 3) for k, v in muscles.items()}
        payload["exercises"] = [ex.to_dict() for ex in filtered]

        return jsonify(payload)
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
        data = request.get_json() or {}
        raw = data.get("exercises", [])
        exercises = []

        if isinstance(raw, dict):
            for items in raw.values():
                exercises.extend(items)
        else:
            exercises = raw

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
                    exercise_id=ex["exercise_id"],
                    sets_done=ex.get("sets") or ex.get("sets_done"),
                    reps_done=ex.get("reps") or ex.get("reps_done"),
                    load_done=ex.get("load") or ex.get("load_done"),
                )
            )

        db.session.commit()
        TrainingSessionService.update_training_load_from_session(session, current_user)
        return jsonify({"id": session.id})
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

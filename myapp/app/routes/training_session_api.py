from flask import Blueprint, jsonify, request
from flask_login import login_required, current_user
from myapp.app.models.training_session import TrainingSession
from myapp.app.services.training_session_service import TrainingSessionService

training_session_api = Blueprint(
    "training_session_api",
    __name__,
    url_prefix="/api/training/session"
)


@training_session_api.post("/start")
@login_required
def start_session():
    payload = request.get_json(silent=True) or {}
    fatigue_before = payload.get("fatigue_before")

    session = TrainingSessionService.start_session(current_user, fatigue_before)

    return jsonify({
        "id": session.id,
        "status": session.status,
        "fatigue_before": session.fatigue_before,
    }), 201


@training_session_api.post("/<int:session_id>/exercise/<exercise_id>")
@login_required
def update_exercise(session_id, exercise_id):
    session = TrainingSession.query.filter_by(
        id=session_id,
        user_id=current_user.id,
        status="active"
    ).first_or_404()

    data = request.get_json() or {}
    se = TrainingSessionService.update_exercise(session, exercise_id, data)

    if not se:
        return jsonify({"error": "exercise not found in session"}), 404

    return jsonify({
        "exercise_id": se.exercise_id,
        "sets_done": se.sets_done,
        "reps_done": se.reps_done,
        "load_done": se.load_done,
        "rpe": se.rpe,
    })


@training_session_api.post("/<int:session_id>/finish")
@login_required
def finish_session(session_id):
    session = TrainingSession.query.filter_by(
        id=session_id,
        user_id=current_user.id,
        status="active"
    ).first_or_404()

    payload = request.get_json(silent=True) or {}
    fatigue_after = payload.get("fatigue_after")

    session = TrainingSessionService.finish_session(session, fatigue_after)

    return jsonify({
        "id": session.id,
        "status": session.status,
        "fatigue_before": session.fatigue_before,
        "fatigue_after": session.fatigue_after,
        "rpe_avg": session.rpe_avg,
    })

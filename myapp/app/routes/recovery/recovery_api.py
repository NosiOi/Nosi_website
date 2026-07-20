from datetime import datetime
from flask import Blueprint, request, jsonify
from myapp.app.services.recovery import (
    SleepService,
    HabitService,
    SnapshotService,
    StatsService,
    RecommendationService,
)

recovery_bp = Blueprint("recovery", __name__, url_prefix="/api/recovery")

sleep_service = SleepService()
habit_service = HabitService()
snapshot_service = SnapshotService()
stats_service = StatsService()


@recovery_bp.post("/sleep")
def add_sleep():
    data = request.json or {}
    user_id = data.get("user_id")
    sleep_start = data.get("sleep_start")
    sleep_end = data.get("sleep_end")

    if user_id is None or sleep_start is None or sleep_end is None:
        return (
            jsonify({"error": "user_id, sleep_start and sleep_end are required"}),
            400,
        )

    try:
        start_dt = datetime.fromisoformat(sleep_start)
        end_dt = datetime.fromisoformat(sleep_end)
    except ValueError:
        return jsonify({"error": "Invalid datetime format"}), 400

    entry = sleep_service.add_sleep(user_id, start_dt, end_dt)
    return (
        jsonify(
            {
                "id": entry.id,
                "duration_minutes": entry.duration_minutes,
                "quality_score": entry.quality_score,
            }
        ),
        201,
    )


@recovery_bp.post("/habits")
def add_habit():
    data = request.json or {}
    user_id = data.get("user_id")
    habit_id = data.get("habit_id")

    if user_id is None or habit_id is None:
        return jsonify({"error": "user_id and habit_id are required"}), 400

    habit = habit_service.add_user_habit(user_id, habit_id)
    return jsonify({"id": habit.id}), 201


@recovery_bp.delete("/habits/<int:user_habit_id>")
def remove_habit(user_habit_id):
    habit = habit_service.remove_user_habit(user_habit_id)
    if not habit:
        return jsonify({"error": "habit not found"}), 404
    return jsonify({"removed": user_habit_id}), 200


@recovery_bp.post("/habits/logs")
def log_habit():
    data = request.json or {}
    user_habit_id = data.get("user_habit_id")

    if user_habit_id is None:
        return jsonify({"error": "user_habit_id is required"}), 400

    log = habit_service.log_habit(user_habit_id)
    if not log:
        return jsonify({"error": "user_habit not found"}), 404
    return jsonify({"logged": log.id}), 200


@recovery_bp.post("/snapshot")
def generate_snapshot():
    data = request.json or {}
    user_id = data.get("user_id")
    if user_id is None:
        return jsonify({"error": "user_id is required"}), 400

    last_training_days = data.get("last_training_days", 0)
    snapshot = snapshot_service.generate_snapshot(user_id, last_training_days)
    return jsonify({"id": snapshot.id}), 201


@recovery_bp.get("/snapshot/<int:user_id>")
def get_snapshot(user_id):
    snapshot = stats_service.get_last_snapshot(user_id)
    if not snapshot:
        return jsonify({"snapshot": None}), 200
    return (
        jsonify(
            {
                "id": snapshot.id,
                "date": str(snapshot.date),
                "sleep_score": snapshot.sleep_score,
                "habit_score": snapshot.habit_score,
                "training_score": snapshot.training_score,
                "energy_score": snapshot.energy_score,
                "recovery_score": snapshot.recovery_score,
                "updated_at": (
                    snapshot.updated_at.isoformat() if snapshot.updated_at else None
                ),
            }
        ),
        200,
    )


@recovery_bp.get("/heatmap/<int:user_id>")
def get_heatmap(user_id):
    days = int(request.args.get("days", 30))
    heatmap = stats_service.get_heatmap(user_id, days)
    return (
        jsonify(
            [
                {
                    "date": str(s.date),
                    "recovery_score": s.recovery_score,
                    "energy_score": s.energy_score,
                }
                for s in heatmap
            ]
        ),
        200,
    )


@recovery_bp.get("/recommendations/<int:user_id>")
def get_recommendations(user_id):
    snapshot = stats_service.get_last_snapshot(user_id)
    if not snapshot:
        return jsonify({"recovery_score": None, "recommendations": []}), 200
    recs = RecommendationService.get_recommendations(
        snapshot.sleep_score, snapshot.habit_score, snapshot.recovery_score
    )
    return (
        jsonify({"recovery_score": snapshot.recovery_score, "recommendations": recs}),
        200,
    )

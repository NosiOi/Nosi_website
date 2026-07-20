from flask import Blueprint, request, jsonify
from myapp.app.services.recovery import (
    SleepService,
    HabitService,
    SnapshotService,
    StatsService,
    RecommendationService,
)

recovery_bp = Blueprint("recovery", __name__, url_prefix="/api/recovery")


@recovery_bp.post("/sleep")
def add_sleep():
    data = request.json
    user_id = data["user_id"]
    sleep_start = data["sleep_start"]
    sleep_end = data["sleep_end"]

    sleep_start = SleepService().sleep_service.parse_datetime(sleep_start)
    sleep_end = SleepService().sleep_service.parse_datetime(sleep_end)

    entry = SleepService().add_sleep(user_id, sleep_start, sleep_end)
    return jsonify({"id": entry.id}), 201


@recovery_bp.post("/habit/add")
def add_habit():
    data = request.json
    user_id = data["user_id"]
    habit_id = data["habit_id"]
    habit = HabitService().add_user_habit(user_id, habit_id)
    return jsonify({"id": habit.id}), 201


@recovery_bp.post("/habit/remove")
def remove_habit():
    data = request.json
    habit_id = data["habit_id"]
    habit = HabitService().remove_user_habit(habit_id)
    return jsonify({"removed": habit_id if habit else None}), 200


@recovery_bp.post("/habit/log")
def log_habit():
    data = request.json
    habit_id = data["habit_id"]
    log = HabitService().log_habit(habit_id)
    return jsonify({"logged": log.id if log else None}), 200


@recovery_bp.post("/snapshot/generate")
def generate_snapshot():
    data = request.json
    user_id = data["user_id"]
    last_training_days = data.get("last_training_days", 0)
    snapshot = SnapshotService().generate_snapshot(user_id, last_training_days)
    return jsonify({"id": snapshot.id}), 201


@recovery_bp.get("/snapshot/<int:user_id>")
def get_snapshot(user_id):
    snapshot = StatsService().get_last_snapshot(user_id)
    if not snapshot:
        return jsonify({"snapshot": None}), 200
    return (
        jsonify(
            {
                "date": str(snapshot.date),
                "sleep_score": snapshot.sleep_score,
                "habit_score": snapshot.habit_score,
                "training_score": snapshot.training_score,
                "energy_score": snapshot.energy_score,
                "recovery_score": snapshot.recovery_score,
            }
        ),
        200,
    )


@recovery_bp.get("/heatmap/<int:user_id>")
def get_heatmap(user_id):
    days = int(request.args.get("days", 30))
    heatmap = StatsService().get_heatmap(user_id, days)
    return (
        jsonify(
            [{"date": str(s.date), "recovery_score": s.recovery_score} for s in heatmap]
        ),
        200,
    )


@recovery_bp.get("/recommendations/<int:user_id>")
def get_recommendations(user_id):
    snapshot = StatsService().get_last_snapshot(user_id)
    if not snapshot:
        return jsonify({"recommendations": []}), 200
    recs = RecommendationService.get_recommendations(
        snapshot.sleep_score, snapshot.habit_score, snapshot.recovery_score
    )
    return jsonify({"recommendations": recs}), 200

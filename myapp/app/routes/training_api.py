from flask import Blueprint, jsonify, request, current_app
from flask_login import login_required, current_user
from myapp.app.services.training_engine_service import TrainingEngineService

training_api = Blueprint("training_api", __name__, url_prefix="/api/training")

@training_api.get("/plan")
@login_required
def get_plan():
    week = int(request.args.get("week", 1))
    try:
        plan = TrainingEngineService.generate_plan(current_user, week)
        return jsonify(plan.to_dict())
    except Exception as e:
        current_app.logger.exception("Error generating training plan")
        return jsonify({"error": "failed to generate plan", "message": str(e)}), 500

@training_api.get("/plan_mock")
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



@training_api.get("/analytics")
@login_required
def get_analytics():
    performance = current_user.performance_state
    recovery = current_user.fatigue_state

    analytics = TrainingEngineService.compute_analytics(performance, recovery)
    return jsonify(analytics)


@training_api.get("/recommendations")
@login_required
def get_recommendations():
    from myapp.app.training_engine.recommendations.weak_point_analysis import WeakPointAnalysis
    from myapp.app.training_engine.recommendations.exercise_recommendations import ExerciseRecommendations
    from myapp.app.training_engine.recommendations.recovery_recommendations import RecoveryRecommendations
    from myapp.app.training_engine.recommendations.nutrition_recommendations import NutritionRecommendations

    profile = TrainingEngineService.build_profile(current_user)

    weak = WeakPointAnalysis.analyze(profile.weak_points, profile.strong_points)
    ex = ExerciseRecommendations.for_weak_points(profile.weak_points, profile.environment)
    rec = RecoveryRecommendations.generate(
        sleep=current_user.fatigue_state.sleep,
        stress=current_user.fatigue_state.stress,
        soreness=current_user.fatigue_state.soreness,
        hydration=current_user.fatigue_state.hydration
    )
    nut = NutritionRecommendations.generate(profile.goal)

    return jsonify({
        "weak_points": weak,
        "exercise_recommendations": ex,
        "recovery": rec,
        "nutrition": nut
    })

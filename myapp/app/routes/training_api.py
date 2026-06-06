from flask import Blueprint, jsonify, request
from flask_login import login_required, current_user
from myapp.app.services.training_engine_service import TrainingEngineService

training_api = Blueprint("training_api", __name__, url_prefix="/api/training")


@training_api.get("/plan")
@login_required
def get_plan():
    week = int(request.args.get("week", 1))
    plan = TrainingEngineService.generate_plan(current_user, week)
    return jsonify(plan.to_dict())


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

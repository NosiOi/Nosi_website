from myapp.app.training_engine.recommendations.nutrition_recommendations import NutritionRecommendations


def test_nutrition_recommendations_gain():
    result = NutritionRecommendations.generate("gain")

    assert any("protein" in rec.lower() for rec in result["nutrition_recommendations"])


def test_nutrition_recommendations_lose():
    result = NutritionRecommendations.generate("lose")

    assert any("calorie" in rec.lower() for rec in result["nutrition_recommendations"])


def test_nutrition_recommendations_maintain():
    result = NutritionRecommendations.generate("maintain")

    assert len(result["nutrition_recommendations"]) > 0

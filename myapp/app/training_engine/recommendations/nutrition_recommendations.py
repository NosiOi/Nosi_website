from typing import Dict


class NutritionRecommendations:
    
    # Provides nutrition suggestions based on user's goal.

    @staticmethod
    def generate(goal: str) -> Dict:
        if goal == "gain":
            return {
                "nutrition_recommendations": [
                    "Increase protein intake.",
                    "Add calorie-dense foods like nuts, rice, and oats.",
                    "Eat 4–5 meals per day."
                ]
            }

        if goal == "lose":
            return {
                "nutrition_recommendations": [
                    "Increase fiber and vegetables.",
                    "Reduce sugar and liquid calories.",
                    "Maintain a moderate calorie deficit."
                ]
            }

        return {
            "nutrition_recommendations": [
                "Maintain balanced macros.",
                "Keep hydration high.",
                "Eat whole foods."
            ]
        }

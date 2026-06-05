from typing import List, Dict


class WeakPointAnalysis:
    
    # Analyzes user's weak points and provides targeted recommendations.

    CRITICAL = {"core", "lower_back"}

    @staticmethod
    def analyze(weak_points: List[str], strong_points: List[str]) -> Dict:
        recommendations = []

        critical = WeakPointAnalysis.CRITICAL.intersection(weak_points)
        if critical:
            recommendations.append(
                f"Critical weak zones detected: {', '.join(critical)}. "
                "Increase frequency of core stability and posterior chain work."
            )

        if "chest" in weak_points:
            recommendations.append("Add more push variations and tempo pushups.")

        if "back" in weak_points:
            recommendations.append("Increase pulling volume: rows, pullups, band pulls.")

        if "legs" in weak_points:
            recommendations.append("Add unilateral work: lunges, split squats, step-ups.")

        if not recommendations:
            recommendations.append("No major weak points detected. Maintain balanced training.")

        return {"weak_point_recommendations": recommendations}

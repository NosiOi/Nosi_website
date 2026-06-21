from typing import List, Dict


class WeakPointAnalysis:
    CRITICAL = {"core", "lower_back"}

    @staticmethod
    def analyze(weak_points: List[str], strong_points: List[str]) -> Dict:
        recs = []

        critical = WeakPointAnalysis.CRITICAL.intersection(weak_points)
        if critical:
            recs.append(
                f"Critical weak zones detected: {', '.join(critical)}. Increase core stability and posterior chain work."
            )

        if "chest" in weak_points:
            recs.append("Add more push variations and tempo pushups.")
        if "back" in weak_points:
            recs.append("Increase pulling volume: rows, pullups, band pulls.")
        if "legs" in weak_points:
            recs.append("Add unilateral work: lunges, split squats, step-ups.")

        if not recs:
            recs.append("No major weak points detected. Maintain balanced training.")

        return {"weak_point_recommendations": recs}

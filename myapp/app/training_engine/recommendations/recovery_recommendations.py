from typing import Dict


class RecoveryRecommendations:
    
    # Provides recovery suggestions based on: sleep, stress, soreness, hydration

    @staticmethod
    def generate(sleep: float, stress: int, soreness: int, hydration: float) -> Dict:
        recs = []

        if sleep < 7:
            recs.append("Increase sleep to at least 7–8 hours for optimal recovery.")

        if stress >= 4:
            recs.append("High stress detected. Add breathing exercises or light stretching.")

        if soreness >= 4:
            recs.append("Severe soreness detected. Reduce intensity and add mobility work.")

        if hydration < 2:
            recs.append("Increase water intake to 2–2.5 liters per day.")

        if not recs:
            recs.append("Recovery is optimal. Continue current routine.")

        return {"recovery_recommendations": recs}

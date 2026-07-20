class RecommendationService:
    @staticmethod
    def get_recommendations(sleep_score, habit_score, recovery_score):
        recs = []
        if sleep_score < 60:
            recs.append("Try to sleep at least 8 hours today")
        if habit_score < 40:
            recs.append("Complete at least one recovery habit")
        if recovery_score < 50:
            recs.append("Focus on hydration and light activity")
        if recovery_score > 85:
            recs.append("You are fully recovered and ready for intense training")
        return recs[:3]

class RecommendationService:
    @staticmethod
    def get_recommendations(snapshot):
        if not snapshot:
            return []

        sleep_score = snapshot.sleep_score or 0
        habit_score = snapshot.habit_score or 0
        recovery_score = snapshot.recovery_score or 0
        energy_score = snapshot.energy_score or 0
        training_score = snapshot.training_score or 0

        recs = []

        if sleep_score < 70:
            recs.append(
                {
                    "text": "Лягти спати раніше та збільшити тривалість сну до 7–9 годин",
                    "priority": "high",
                    "icon": "moon",
                }
            )

        if training_score > 75 and sleep_score < 80:
            recs.append(
                {
                    "text": "Зменшити інтенсивність тренувань або додати день відпочинку",
                    "priority": "high",
                    "icon": "training",
                }
            )

        if habit_score < 50:
            recs.append(
                {
                    "text": "Виконати хоча б одну базову звичку для відновлення",
                    "priority": "medium",
                    "icon": "habits",
                }
            )

        if energy_score < 60:
            recs.append(
                {
                    "text": "Сконцентруватися на легкій активності, прогулянці або розтяжці",
                    "priority": "medium",
                    "icon": "rest",
                }
            )

        if recovery_score < 50:
            recs.append(
                {
                    "text": "Сфокусуватися на сні, гідратації та уникати важких тренувань",
                    "priority": "high",
                    "icon": "water",
                }
            )

        if recovery_score > 85 and sleep_score >= 80 and training_score <= 60:
            recs.append(
                {
                    "text": "Рівень відновлення високий — можна планувати інтенсивне тренування",
                    "priority": "low",
                    "icon": "heart_pulse",
                }
            )

        return recs[:5]

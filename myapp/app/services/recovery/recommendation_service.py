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

        if sleep_score < 60:
            recs.append(
                {"text": "Лягти спати раніше", "priority": "high", "icon": "moon"}
            )

        if habit_score < 40:
            recs.append(
                {
                    "text": "Виконати хоча б одну звичку",
                    "priority": "medium",
                    "icon": "habits",
                }
            )

        if recovery_score < 50:
            recs.append(
                {
                    "text": "Пити більше води та уникати важких тренувань",
                    "priority": "high",
                    "icon": "water",
                }
            )

        if energy_score < 50:
            recs.append(
                {
                    "text": "Зробити легку розтяжку або прогулянку",
                    "priority": "medium",
                    "icon": "rest",
                }
            )

        if training_score == 0:
            recs.append(
                {
                    "text": "Додати легку активність для підтримки тонусу",
                    "priority": "low",
                    "icon": "energy",
                }
            )

        if recovery_score > 85:
            recs.append(
                {
                    "text": "Ви повністю відновлені — можна тренуватись інтенсивно",
                    "priority": "low",
                    "icon": "heart_pulse",
                }
            )

        return recs[:5]

from myapp.app.services.recovery.constants import RecoveryTrigger


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

        if recovery_score < 50:
            recs.append(
                {
                    "text": "Рівень відновлення низький — зменшити навантаження та сфокусуватись на сні й базових звичках",
                    "priority": "high",
                    "icon": "alert",
                    "trigger": RecoveryTrigger.LOW_RECOVERY.value,
                }
            )

        if sleep_score < 70:
            recs.append(
                {
                    "text": "Лягти спати раніше та збільшити тривалість сну до рекомендованого діапазону",
                    "priority": "high",
                    "icon": "moon",
                    "trigger": RecoveryTrigger.SLEEP_DEFICIT.value,
                }
            )

        if training_score > 80 and recovery_score < 70:
            recs.append(
                {
                    "text": "Після інтенсивного тренування додати день відпочинку або легку активність замість важких вправ",
                    "priority": "high",
                    "icon": "training",
                    "trigger": RecoveryTrigger.AFTER_TRAINING.value,
                }
            )

        if habit_score < 50:
            recs.append(
                {
                    "text": "Виконати хоча б одну звичку для відновлення: гідратація, розтяжка, прогулянка або дихальні вправи",
                    "priority": "medium",
                    "icon": "habits",
                    "trigger": RecoveryTrigger.RECOVERY.value,
                }
            )

        if energy_score < 60:
            recs.append(
                {
                    "text": "Сконцентруватися на легкій активності, прогулянці або розтяжці замість інтенсивних тренувань",
                    "priority": "medium",
                    "icon": "rest",
                    "trigger": RecoveryTrigger.LOW_ENERGY.value,
                }
            )

        if recovery_score > 85 and sleep_score >= 80 and training_score <= 70:
            recs.append(
                {
                    "text": "Рівень відновлення високий — можна планувати інтенсивне тренування з акцентом на прогрес",
                    "priority": "low",
                    "icon": "heart_pulse",
                    "trigger": RecoveryTrigger.AFTER_TRAINING.value,
                }
            )

        return recs[:5]

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

        if sleep_score < 70:
            recs.append(
                {
                    "text": "Лягти спати раніше та наблизити тривалість сну до вашої оптимальної норми.",
                    "priority": "high",
                    "icon": "moon",
                    "trigger": RecoveryTrigger.SLEEP_DEFICIT.value,
                }
            )

        if recovery_score < 50:
            recs.append(
                {
                    "text": "Рівень відновлення низький — сфокусуйся на сні, гідратації та зменшенні навантаження.",
                    "priority": "high",
                    "icon": "water",
                    "trigger": RecoveryTrigger.LOW_RECOVERY.value,
                }
            )

        if energy_score < 60:
            recs.append(
                {
                    "text": "Обрати легку активність: прогулянку, розтяжку або мобілізацію замість важкого тренування.",
                    "priority": "medium",
                    "icon": "rest",
                    "trigger": RecoveryTrigger.LOW_ENERGY.value,
                }
            )

        if training_score >= 80 and recovery_score < 70:
            recs.append(
                {
                    "text": "Після інтенсивного тренування варто додати день відпочинку або знизити навантаження.",
                    "priority": "high",
                    "icon": "training",
                    "trigger": RecoveryTrigger.AFTER_TRAINING.value,
                }
            )

        if habit_score < 50:
            recs.append(
                {
                    "text": "Виконати хоча б одну базову звичку для відновлення (сон, вода, розтяжка, ходьба).",
                    "priority": "medium",
                    "icon": "habits",
                    "trigger": RecoveryTrigger.RECOVERY.value,
                }
            )

        if recovery_score > 85 and sleep_score >= 80 and energy_score >= 75:
            recs.append(
                {
                    "text": "Рівень відновлення високий — можна планувати інтенсивне тренування.",
                    "priority": "low",
                    "icon": "heart_pulse",
                    "trigger": RecoveryTrigger.RECOVERY.value,
                }
            )

        return recs[:5]

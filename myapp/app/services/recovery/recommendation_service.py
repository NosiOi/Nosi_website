from myapp.app.services.training_load_service import TrainingLoadService
from myapp.app.services.recovery.constants import (
    TRAINING_LOAD_HEAVY,
    TRAINING_LOAD_VERY_HEAVY,
    RecoveryTrigger,
)


class RecommendationService:
    def __init__(self):
        self.training_load = TrainingLoadService()

    def get_recommendations(self, snapshot):
        if not snapshot:
            return []

        sleep_score = snapshot.sleep_score or 0
        habit_score = snapshot.habit_score or 0
        recovery_score = snapshot.recovery_score or 0
        energy_score = snapshot.energy_score or 0

        daily_load = self.training_load.get_daily_load(snapshot.user_id)

        recs = []

        if sleep_score < 70:
            recs.append(
                {
                    "text": "Лягти спати раніше та збільшити тривалість сну до 7–9 годин",
                    "priority": "high",
                    "icon": "moon",
                    "trigger": RecoveryTrigger.SLEEP_DEFICIT.value,
                }
            )

        if daily_load >= TRAINING_LOAD_HEAVY and recovery_score < 80:
            recs.append(
                {
                    "text": "Після важкого тренування варто зменшити інтенсивність або додати день відпочинку",
                    "priority": "high",
                    "icon": "training",
                    "trigger": RecoveryTrigger.AFTER_HEAVY_TRAINING.value,
                }
            )

        if habit_score < 50:
            recs.append(
                {
                    "text": "Виконати хоча б одну базову звичку для відновлення (вода, розтяжка, прогулянка)",
                    "priority": "medium",
                    "icon": "habits",
                    "trigger": RecoveryTrigger.LOW_RECOVERY.value,
                }
            )

        if energy_score < 60:
            recs.append(
                {
                    "text": "Сконцентруватися на легкій активності, прогулянці або розтяжці замість важких тренувань",
                    "priority": "medium",
                    "icon": "rest",
                    "trigger": RecoveryTrigger.LOW_ENERGY.value,
                }
            )

        if recovery_score < 50:
            recs.append(
                {
                    "text": "Сфокусуватися на сні, гідратації та уникати важких тренувань до покращення відновлення",
                    "priority": "high",
                    "icon": "water",
                    "trigger": RecoveryTrigger.LOW_RECOVERY.value,
                }
            )

        if (
            recovery_score > 85
            and sleep_score >= 80
            and daily_load < TRAINING_LOAD_HEAVY
        ):
            recs.append(
                {
                    "text": "Рівень відновлення високий — можна планувати інтенсивне тренування",
                    "priority": "low",
                    "icon": "heart_pulse",
                    "trigger": RecoveryTrigger.AFTER_HEAVY_TRAINING.value,
                }
            )

        return recs[:5]

from typing import List, Dict, Any

from myapp.app.services.training_load_service import TrainingLoadService
from myapp.app.services.recovery.constants import (
    TRAINING_LOAD_HIGH,
    TRAINING_LOAD_VERY_HIGH,
)


class RecommendationService:
    def __init__(self) -> None:
        self.training_load = TrainingLoadService()

    @staticmethod
    def _base_recommendations(
        sleep_score: int,
        habit_score: int,
        recovery_score: int,
        energy_score: int,
    ) -> List[Dict[str, Any]]:
        recs: List[Dict[str, Any]] = []

        if sleep_score < 70:
            recs.append(
                {
                    "text": "Лягти спати раніше та збільшити тривалість сну до 7–9 годин",
                    "priority": "high",
                    "icon": "moon",
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

        if recovery_score > 85 and sleep_score >= 80:
            recs.append(
                {
                    "text": "Рівень відновлення високий — можна планувати інтенсивне тренування",
                    "priority": "low",
                    "icon": "heart_pulse",
                }
            )

        return recs

    def get_recommendations(self, snapshot) -> List[Dict[str, Any]]:
        if not snapshot:
            return []

        sleep_score = snapshot.sleep_score or 0
        habit_score = snapshot.habit_score or 0
        recovery_score = snapshot.recovery_score or 0
        energy_score = snapshot.energy_score or 0

        recs = self._base_recommendations(
            sleep_score,
            habit_score,
            recovery_score,
            energy_score,
        )

        daily_load = self.training_load.get_daily_load(snapshot.user_id)

        if daily_load >= TRAINING_LOAD_VERY_HIGH and recovery_score < 70:
            recs.append(
                {
                    "text": "Після дуже важкого тренування варто зменшити навантаження або зробити день відпочинку",
                    "priority": "high",
                    "icon": "training",
                }
            )
        elif daily_load >= TRAINING_LOAD_HIGH and recovery_score < 80:
            recs.append(
                {
                    "text": "Навантаження було високим — зверни увагу на сон та гідратацію",
                    "priority": "medium",
                    "icon": "training",
                }
            )

        return recs[:5]

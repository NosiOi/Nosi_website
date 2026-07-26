from typing import List, Dict

from myapp.app.services.recovery.constants import RecoveryTrigger
from myapp.app.services.recovery.constants import (
    TRAINING_LOAD_HEAVY,
    TRAINING_LOAD_VERY_HEAVY,
)


class RecommendationService:
    """Generate recovery recommendations."""

    def build_recommendations(
        self,
        sleep_score: int,
        recovery_score: int,
        energy_score: int,
        habit_score: int,
        daily_load: float,
    ) -> List[Dict]:
        recs: List[Dict] = []

        if sleep_score < 70:
            recs.append(
                {
                    "trigger": RecoveryTrigger.SLEEP_DEFICIT.value,
                    "priority": "high",
                    "icon": "moon",
                    "text": "Спробуй лягти раніше — останні ночі виглядають як недосип.",
                }
            )

        if recovery_score < 40:
            recs.append(
                {
                    "trigger": RecoveryTrigger.LOW_RECOVERY.value,
                    "priority": "high",
                    "icon": "heart",
                    "text": "Рівень відновлення низький — варто зменшити навантаження.",
                }
            )

        if energy_score < 60:
            recs.append(
                {
                    "trigger": RecoveryTrigger.LOW_ENERGY.value,
                    "priority": "medium",
                    "icon": "battery",
                    "text": "Енергія нижча за норму — зверни увагу на сон і гідратацію.",
                }
            )

        if habit_score < 50:
            recs.append(
                {
                    "trigger": RecoveryTrigger.RECOVERY.value,
                    "priority": "medium",
                    "icon": "leaf",
                    "text": "Виконання recovery-звичок низьке — додай хоча б одну просту дію.",
                }
            )

        if daily_load > TRAINING_LOAD_VERY_HEAVY:
            recs.append(
                {
                    "trigger": RecoveryTrigger.AFTER_TRAINING.value,
                    "priority": "high",
                    "icon": "dumbbell",
                    "text": "Останнє тренування було дуже важким — заплануй більше сну.",
                }
            )
        elif daily_load > TRAINING_LOAD_HEAVY:
            recs.append(
                {
                    "trigger": RecoveryTrigger.AFTER_TRAINING.value,
                    "priority": "medium",
                    "icon": "dumbbell",
                    "text": "Навантаження вище середнього — додай легке відновлення.",
                }
            )

        priority_order = {"high": 0, "medium": 1, "low": 2}
        recs.sort(key=lambda r: priority_order[r["priority"]])

        return recs[:5]

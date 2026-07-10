from typing import List
from datetime import date, timedelta
from myapp.app.training_engine.training_analysis.dto import DiversityResult
from myapp.app.training_engine.training_analysis.constants import (
    LOW_DIVERSITY_THRESHOLD,
    MEDIUM_DIVERSITY_THRESHOLD,
)


def analyse_diversity(
    sessions: List, target_day: date, days: int = 28
) -> DiversityResult:
    start = target_day - timedelta(days=days)
    window = [
        s
        for s in sessions
        if s.started_at and start <= s.started_at.date() <= target_day
    ]

    names: List[str] = []

    for s in window:
        for se in s.exercises or []:
            if se.exercise_name:
                names.append(se.exercise_name)

    total = len(names)
    unique = len(set(names))

    if total == 0:
        return {
            "status": "unknown",
            "score": 0.0,
            "unique_exercises": 0,
            "total_exercises": 0,
            "message": "no exercise data",
        }

    score = unique / total

    if score > MEDIUM_DIVERSITY_THRESHOLD:
        status = "high"
    elif score > LOW_DIVERSITY_THRESHOLD:
        status = "medium"
    else:
        status = "low"

    return {
        "status": status,
        "score": score,
        "unique_exercises": unique,
        "total_exercises": total,
        "message": "exercise diversity analysed",
    }

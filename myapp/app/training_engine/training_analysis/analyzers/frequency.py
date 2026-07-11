from typing import Mapping, Dict, List
from datetime import date, timedelta
from myapp.app.training_engine.training_analysis.dto import FrequencyResult
from myapp.app.training_engine.training_analysis.analyzers.utils import primary_muscles
from myapp.app.training_engine.models.exercise import Exercise


def analyse_frequency(
    sessions: List,
    target_day: date,
    exercise_map: Mapping[object, Exercise],
    days: int = 28,
) -> FrequencyResult:
    start = target_day - timedelta(days=days)
    window = [
        s
        for s in sessions
        if s.started_at and start <= s.started_at.date() <= target_day
    ]

    names: List[str] = []

    for s in window:
        for se in s.exercises or []:
            ex = exercise_map.get(se.exercise_id)
            if ex:
                names.append(ex.name)

    total = len(names)
    unique = len(set(names))

    counts = {}
    for name in names:
        counts[name] = counts.get(name, 0) + 1

    return {
        "total": total,
        "unique": unique,
        "counts": counts,  # ← додано
        "message": "frequency analysed",
    }

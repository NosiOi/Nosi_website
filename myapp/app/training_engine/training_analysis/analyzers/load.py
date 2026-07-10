from typing import List
from datetime import date, timedelta
from myapp.app.training_engine.training_analysis.dto import LoadResult


def analyse_load(sessions: List, target_day: date, days: int = 7) -> LoadResult:
    start = target_day - timedelta(days=days)
    window = [
        s
        for s in sessions
        if s.started_at and start <= s.started_at.date() <= target_day
    ]

    if not window:
        return {
            "status": "unknown",
            "avg_rpe": 0.0,
            "sessions_count": 0,
            "message": "no load data",
        }

    rpes = [float(getattr(s, "rpe", 0.0) or 0.0) for s in window]
    avg_rpe = sum(rpes) / len(rpes) if rpes else 0.0

    if avg_rpe >= 8:
        status = "very_hard"
    elif avg_rpe >= 6:
        status = "hard"
    elif avg_rpe >= 4:
        status = "moderate"
    else:
        status = "easy"

    return {
        "status": status,
        "avg_rpe": avg_rpe,
        "sessions_count": len(window),
        "message": "training load analysed",
    }

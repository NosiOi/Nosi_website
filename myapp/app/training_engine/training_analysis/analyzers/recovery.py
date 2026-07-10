from typing import List
from datetime import date, timedelta
from myapp.app.training_engine.training_analysis.dto import RecoveryResult


def analyse_recovery(sessions: List, target_day: date, days: int = 7) -> RecoveryResult:
    start = target_day - timedelta(days=days)
    window = [
        s
        for s in sessions
        if s.started_at and start <= s.started_at.date() <= target_day
    ]

    sleep_values: List[float] = []
    fatigue_values: List[float] = []

    for s in window:
        sleep = getattr(s, "sleep_hours", None)
        fatigue = getattr(s, "fatigue", None)
        if sleep is not None:
            sleep_values.append(float(sleep))
        if fatigue is not None:
            fatigue_values.append(float(fatigue))

    sleep_avg = sum(sleep_values) / len(sleep_values) if sleep_values else 0.0
    fatigue_avg = sum(fatigue_values) / len(fatigue_values) if fatigue_values else 0.0

    if sleep_avg >= 7 and fatigue_avg <= 3:
        status = "good"
    elif sleep_avg >= 6 and fatigue_avg <= 5:
        status = "medium"
    else:
        status = "low"

    return {
        "status": status,
        "sleep_hours_avg": sleep_avg,
        "fatigue_avg": fatigue_avg,
        "message": "recovery analysed",
    }

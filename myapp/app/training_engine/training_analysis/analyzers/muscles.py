from typing import Dict, List
from datetime import date, timedelta
from myapp.app.training_engine.training_analysis.dto import MuscleResult


def analyse_muscles(sessions: List, target_day: date, days: int = 14) -> MuscleResult:
    start = target_day - timedelta(days=days)
    window = [
        s
        for s in sessions
        if s.started_at and start <= s.started_at.date() <= target_day
    ]

    totals: Dict[str, float] = {}

    for s in window:
        for m, v in (s.muscle_loads or {}).items():
            totals[m] = totals.get(m, 0.0) + float(v or 0.0)

    if not totals:
        return {
            "weak": [],
            "overloaded": [],
            "balanced": [],
            "totals": {},
            "balance_ratio": {},
            "message": "no muscle data",
        }

    values = sorted(totals.values())
    mid = len(values) // 2
    median = (
        values[mid] if len(values) % 2 == 1 else (values[mid - 1] + values[mid]) / 2
    )

    weak: List[str] = []
    overloaded: List[str] = []
    balanced: List[str] = []
    ratio: Dict[str, float] = {}

    for m, v in totals.items():
        r = v / median if median > 0 else 1.0
        ratio[m] = r

        if v < median * 0.7:
            weak.append(m)
        elif v > median * 1.35:
            overloaded.append(m)
        else:
            balanced.append(m)

    return {
        "weak": weak,
        "overloaded": overloaded,
        "balanced": balanced,
        "totals": totals,
        "balance_ratio": ratio,
        "message": "muscle balance analysed",
    }

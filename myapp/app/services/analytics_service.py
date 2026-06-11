from collections import defaultdict
from typing import Callable, Dict, Iterable, List, Tuple, Any


def _safe_int(val, default=1):
    try:
        if isinstance(val, (int, float)):
            return int(val)
        s = str(val)
        return int(s) if s.isdigit() else default
    except Exception:
        return default


def compute_muscle_load_from_session(session_payload: Dict[str, Any], exercise_lookup: Callable[[int], Any]) -> Dict[str, float]:
    """
    Compute raw muscle load scores for a single session payload.

    session_payload: dict with key "exercises": list of entries, each entry contains:
      - id or exercise_id
      - sets (int)
      - reps (int)
      - optional weight (ignored for MVP)
    exercise_lookup: callable(ex_id) -> Exercise-like object

    Exercise-like object:
      - may have attribute `exercise_muscles`: iterable of objects with `.muscle.slug`, optional `.load_percent`, optional `.is_primary`
      - or may have attribute `muscles`: iterable of Muscle-like objects with `.slug`

    Returns: dict {muscle_slug: score}
    """
    muscle_scores = defaultdict(float)
    exercises = session_payload.get("exercises", []) or []

    for ex_entry in exercises:
        ex_id = ex_entry.get("id") or ex_entry.get("exercise_id")
        if not ex_id:
            continue
        ex = exercise_lookup(ex_id)
        if not ex:
            continue

        sets = _safe_int(ex_entry.get("sets", 1), 1)
        reps = _safe_int(ex_entry.get("reps", 1), 1)
        work = sets * reps

        if hasattr(ex, "exercise_muscles") and getattr(ex, "exercise_muscles"):
            for em in ex.exercise_muscles:
                m = getattr(em, "muscle", None)
                if not m:
                    continue
                mslug = getattr(m, "slug", None)
                if not mslug:
                    continue
                load = getattr(em, "load_percent", None)
                if load is None:
                    load = 60 if getattr(em, "is_primary", False) else 20
                score = (load or 0) * work / 100.0
                muscle_scores[mslug] += score
        else:
            muscles = getattr(ex, "muscles", None) or []
            muscles = list(muscles)
            if not muscles:
                continue
            per = work / max(1, len(muscles))
            for m in muscles:
                mslug = getattr(m, "slug", None)
                if not mslug:
                    continue
                muscle_scores[mslug] += per

    return dict(muscle_scores)


def compute_muscle_load_from_sessions(sessions: Iterable[Dict[str, Any]], exercise_lookup: Callable[[int], Any]) -> Dict[str, float]:
    """
    Aggregate muscle load across multiple sessions.

    sessions: iterable of session_payload dicts (same format as compute_muscle_load_from_session)
    exercise_lookup: callable(ex_id) -> Exercise-like object

    Returns raw aggregated scores {muscle_slug: score}
    """
    agg = defaultdict(float)
    for s in sessions:
        per = compute_muscle_load_from_session(s, exercise_lookup)
        for k, v in per.items():
            agg[k] += v
    return dict(agg)


def normalize_scores(raw_scores: Dict[str, float]) -> Dict[str, float]:
    """
    Normalize raw scores to relative proportions summing to 1.0 (or 0 if empty).
    Returns dict {muscle_slug: normalized_value}
    """
    total = sum(raw_scores.values())
    if total <= 0:
        return {k: 0.0 for k in raw_scores.keys()}
    return {k: round(v / total, 4) for k, v in raw_scores.items()}


def compute_weekly_report(sessions: Iterable[Dict[str, Any]], exercise_lookup: Callable[[int], Any]) -> Dict[str, Any]:
    #Convenience function returning both raw and normalized muscle load for given sessions.
    raw = compute_muscle_load_from_sessions(sessions, exercise_lookup)
    normalized = normalize_scores(raw)
    return {"raw": raw, "normalized": normalized}

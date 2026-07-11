from datetime import date
from typing import List, Mapping, Dict, Any
from myapp.app.training_engine.models.exercise import Exercise

from myapp.app.training_engine.training_analysis.dto import (
    RecommendationPackage,
    RecommendationExercise,
    MuscleResult,
    PatternResult,
    ProgressionResult,
    DiversityResult,
    FrequencyResult,
    LoadResult,
    RecoveryResult,
)
from myapp.app.training_engine.training_analysis.analyzers.muscles import (
    analyse_muscles,
)
from myapp.app.training_engine.training_analysis.analyzers.patterns import (
    analyse_patterns,
)
from myapp.app.training_engine.training_analysis.analyzers.progression import (
    analyse_progression,
)
from myapp.app.training_engine.training_analysis.analyzers.load import analyse_load
from myapp.app.training_engine.training_analysis.analyzers.recovery import (
    analyse_recovery,
)
from myapp.app.training_engine.training_analysis.analyzers.diversity import (
    analyse_diversity,
)
from myapp.app.training_engine.training_analysis.analyzers.frequency import (
    analyse_frequency,
)
from myapp.app.training_engine.training_analysis.analyzers.utils import (
    pattern_key,
    primary_muscles,
    movement_pattern,
)
from myapp.app.training_engine.training_analysis.constants import (
    WEAK_MUSCLE_SCORE,
    OVERLOAD_PENALTY,
    PATTERN_SCORE,
    DIFFICULTY_PENALTY,
    DIVERSITY_BONUS,
    FREQUENCY_HIGH,
    FREQUENCY_LOW,
    FREQUENCY_PENALTY,
    FREQUENCY_BONUS,
    PROGRESSION_SCORE,
    PLATEAU_SCORE,
    PROGRESSION_PLATEAU_THRESHOLD,  # ← додано
    USER_LEVEL_BEGINNER,
    SUMMARY_PRIORITY,
)


def _reason_muscles(ex: Exercise, muscles: MuscleResult) -> List[str]:
    reasons: List[str] = []
    prim = primary_muscles(ex)
    for m in muscles["weak"]:
        if m.lower() in prim:
            reasons.append("improves weak muscle group")
    return reasons


def _reason_patterns(ex: Exercise, patterns: PatternResult) -> List[str]:
    reasons: List[str] = []
    mp = movement_pattern(ex)
    if mp in patterns["weak_patterns"]:
        reasons.append("improves weak movement pattern")
    return reasons


def _reason_progression(ex: Exercise, progression: ProgressionResult) -> List[str]:
    reasons: List[str] = []
    prog = progression["details"].get(str(ex.id))
    if not prog:
        return reasons
    change = prog["change"]
    if change < 0:
        reasons.append("helps reverse regression")
    elif abs(change) < PROGRESSION_PLATEAU_THRESHOLD:
        reasons.append("helps break plateau")
    return reasons


def _reason_diversity(diversity: DiversityResult) -> List[str]:
    if diversity["status"] == "low":
        return ["adds exercise variety"]
    return []


def _reasons(
    ex: Exercise,
    muscles: MuscleResult,
    patterns: PatternResult,
    diversity: DiversityResult,
    progression: ProgressionResult,
) -> List[str]:
    reasons: List[str] = []
    reasons.extend(_reason_muscles(ex, muscles))
    reasons.extend(_reason_patterns(ex, patterns))
    reasons.extend(_reason_progression(ex, progression))
    reasons.extend(_reason_diversity(diversity))

    reasons = list(dict.fromkeys(reasons))

    if not reasons:
        reasons.append("general strength exercise")

    return reasons


def _score_muscles(ex: Exercise, muscles: MuscleResult) -> float:
    score = 0.0
    prim = primary_muscles(ex)
    for m in muscles["weak"]:
        if m.lower() in prim:
            score += WEAK_MUSCLE_SCORE
    for m in muscles["overloaded"]:
        if m.lower() in prim:
            score -= OVERLOAD_PENALTY
    return score


def _score_patterns(ex: Exercise, patterns: PatternResult) -> float:
    score = 0.0
    mp = movement_pattern(ex)
    if mp in patterns["weak_patterns"]:
        score += PATTERN_SCORE
    if mp in patterns["overloaded_patterns"]:
        score -= PATTERN_SCORE
    return score


def _score_difficulty(ex: Exercise, user_level: str) -> float:
    score = 0.0
    difficulty = float(ex.difficulty or 1)
    if user_level == USER_LEVEL_BEGINNER and difficulty >= 4:
        score -= DIFFICULTY_PENALTY
    return score


def _score_diversity(diversity: DiversityResult) -> float:
    return DIVERSITY_BONUS if diversity["status"] == "low" else 0.0


def _score_progression(ex: Exercise, progression: ProgressionResult) -> float:
    score = 0.0
    prog = progression["details"].get(str(ex.id))
    if not prog:
        return score
    change = prog["change"]
    if change < 0:
        score += PROGRESSION_SCORE
    elif abs(change) < PROGRESSION_PLATEAU_THRESHOLD:
        score += PLATEAU_SCORE
    return score


def _score_frequency(ex: Exercise, frequency: FrequencyResult) -> float:
    score = 0.0
    freq_counts = frequency["counts"]
    prim = primary_muscles(ex)
    for m in prim:
        c = freq_counts.get(m, 0)
        if c >= FREQUENCY_HIGH:
            score -= FREQUENCY_PENALTY
        elif c <= FREQUENCY_LOW:
            score += FREQUENCY_BONUS
    return score


def _score(
    ex: Exercise,
    muscles: MuscleResult,
    patterns: PatternResult,
    diversity: DiversityResult,
    progression: ProgressionResult,
    frequency: FrequencyResult,
    user_level: str,
) -> float:
    score = 0.0
    score += _score_muscles(ex, muscles)
    score += _score_patterns(ex, patterns)
    score += _score_difficulty(ex, user_level)
    score += _score_diversity(diversity)
    score += _score_progression(ex, progression)
    score += _score_frequency(ex, frequency)
    return score


def _build_summary(
    muscles: MuscleResult,
    patterns: PatternResult,
    load: LoadResult,
    recovery: RecoveryResult,
) -> str:
    messages: List[tuple[str, str]] = []

    if muscles["weak"]:
        messages.append(("muscles", "some muscles are undertrained"))
    if patterns["weak_patterns"]:
        messages.append(("patterns", "some movement patterns are weak"))
    if load["status"] in {"hard", "very_hard"}:
        messages.append(("load", "training load is high"))
    if recovery["status"] == "low":
        messages.append(("recovery", "recovery should be prioritized"))

    if not messages:
        return "training looks ok."

    messages.sort(key=lambda m: SUMMARY_PRIORITY[m[0]], reverse=True)
    return ". ".join(m[1] for m in messages) + "."


def build_recommendations(
    user: Any, sessions: List, target_day: date
) -> RecommendationPackage:
    exercises: List[Exercise] = Exercise.query.all()
    exercise_map: Mapping[object, Exercise] = {ex.id: ex for ex in exercises}

    weight = float(getattr(user, "weight", 70) or 70)
    user_level = getattr(user, "level", "intermediate").lower()

    muscles = analyse_muscles(sessions, target_day)
    patterns = analyse_patterns(sessions, target_day, exercise_map, user_weight=weight)
    progression = analyse_progression(
        sessions, target_day, exercise_map, user_weight=weight
    )
    load = analyse_load(sessions, target_day)
    recovery = analyse_recovery(sessions, target_day)
    diversity = analyse_diversity(sessions, target_day)
    frequency = analyse_frequency(sessions, target_day, exercise_map)

    scored: List[tuple[float, Exercise]] = []
    for ex in exercises:
        if not ex.muscles_primary:
            continue
        s = _score(ex, muscles, patterns, diversity, progression, frequency, user_level)
        if s > 0:
            scored.append((s, ex))

    scored.sort(key=lambda x: x[0], reverse=True)

    recommended: List[RecommendationExercise] = []
    used_patterns = set()

    for score, ex in scored:
        mp = pattern_key(ex.movement_pattern)
        if mp in used_patterns:
            continue

        reasons = _reasons(ex, muscles, patterns, diversity, progression)
        recommended.append(
            {"exercise": ex.name, "reasons": reasons, "score": round(score, 1)}
        )

        used_patterns.add(mp)

        if len(recommended) == 3:
            break

    summary = _build_summary(muscles, patterns, load, recovery)

    return {
        "load": load,
        "muscles": muscles,
        "patterns": patterns,
        "progression": progression,
        "recovery": recovery,
        "diversity": diversity,
        "frequency": frequency,
        "recommended_exercises": recommended,
        "summary": summary,
    }

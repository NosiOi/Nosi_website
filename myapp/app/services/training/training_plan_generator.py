import json
from typing import Dict, Any, List

from myapp.app import db
from myapp.app.models.training_plan import TrainingPlan
from myapp.app.models.fitness_assessment import FitnessAssessment
from myapp.app.models.exercise import Exercise
from myapp.app.models.equipment import Equipment

from .strength_assessment import StrengthIndex
from .training_math import calc_sets, calc_reps, calc_rest


def _compute_experience_factor(user) -> float:
    months = getattr(user, "training_experience_months", 0) or 0
    return min(max(months, 0) / 36.0, 1.0)


def _get_user_equipment_ids(user) -> List[int]:
    eq = getattr(user, "equipment", None)
    if not eq:
        return []
    return [e.id for e in eq]


def _select_exercises(
    muscle_group: str,
    strength_index_value: float,
    experience_factor: float,
    equipment_ids: List[int],
    limit: int = 5,
) -> List[Exercise]:

    query = Exercise.query.filter(
        Exercise.muscle_group == muscle_group,
        Exercise.min_strength_index <= strength_index_value,
        Exercise.min_experience <= experience_factor,
    )

    if equipment_ids:
        query = (
            query.join(Exercise.equipment)
            .filter(Equipment.id.in_(equipment_ids))
            .distinct()
        )
    else:
        query = (
            query.join(Exercise.equipment)
            .filter(Equipment.name == "bodyweight")
            .distinct()
        )

    query = query.order_by(db.func.abs(Exercise.difficulty - strength_index_value))

    return query.limit(limit).all()


def generate_training_plan_for_user(
    user,
    assessment: FitnessAssessment,
    program_type: str = "full_body",
    location: str = "home",
) -> TrainingPlan:

    si = StrengthIndex(
        si_push=assessment.si_push,
        si_squat=assessment.si_squat,
        si_core=assessment.si_core,
    )

    strength_indices = {
        "push": si.si_push,
        "legs": si.si_squat,
        "core": si.si_core,
        "total": (si.si_push + si.si_squat + si.si_core) / 3.0,
    }

    experience_factor = _compute_experience_factor(user)
    equipment_ids = _get_user_equipment_ids(user)

    days_per_week = getattr(user, "trainings_per_week", 3) or 3
    days_per_week = max(1, min(days_per_week, 7))

    if program_type == "full_body":
        day_muscle_groups = ["full"] * days_per_week
    else:
        base_pattern = ["push", "legs", "core"]
        day_muscle_groups = [
            base_pattern[i % len(base_pattern)] for i in range(days_per_week)
        ]

    plan_struct = {
        "program_type": program_type,
        "location": location,
        "days_per_week": days_per_week,
        "days": [],
    }

    for day_index, mg in enumerate(day_muscle_groups, start=1):

        si_used = (
            strength_indices.get(mg, strength_indices["total"])
            if mg != "full"
            else strength_indices["total"]
        )

        exercises = _select_exercises(
            muscle_group=mg if mg != "full" else "full",
            strength_index_value=si_used,
            experience_factor=experience_factor,
            equipment_ids=equipment_ids,
            limit=5,
        )

        day_data = {
            "day_index": day_index,
            "name": f"Day {day_index} — {mg}",
            "exercises": [],
        }

        for ex in exercises:
            sets = calc_sets(3, strength_indices["total"])
            reps = calc_reps(10, strength_indices["total"])
            rest = calc_rest(90, strength_indices["total"])

            day_data["exercises"].append(
                {
                    "name": ex.name,
                    "muscle_group": ex.muscle_group,
                    "sets": sets,
                    "reps": reps,
                    "rest_seconds": rest,
                    "notes": "RIR 2–3",
                }
            )

        plan_struct["days"].append(day_data)

    plan_json = json.dumps(plan_struct, ensure_ascii=False)

    training_plan = TrainingPlan(
        user_id=user.id,
        plan_json=plan_json,
    )
    db.session.add(training_plan)
    db.session.commit()

    return training_plan

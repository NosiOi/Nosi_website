import json
from typing import Dict, Any

from myapp.app.models.training_plan import TrainingPlan
from myapp.app.models.fitness_assessment import FitnessAssessment
from myapp.app import db

from .strength_assessment import StrengthIndex
from .training_math import calc_sets, calc_reps, calc_rest
from .training_templates import get_program_template, ProgramType, TrainingLocation


def _choose_exercise_variant_by_strength(
    exercise_variants, strength_index: float
) -> Any:
    """
    strength_index ~ 0.0–2.0
    мапимо його на level вправи
    """
    max_level = max(ev.level for ev in exercise_variants)
    normalized = max(0.0, min(strength_index / 1.0, 1.0))
    target_level = round(normalized * max_level)

    candidates = sorted(exercise_variants, key=lambda ev: abs(ev.level - target_level))
    return candidates[0]


def generate_training_plan_for_user(
    user,
    assessment: FitnessAssessment,
    program_type: ProgramType = "full_body",
    location: TrainingLocation = "home",
) -> TrainingPlan:
    """
    Генерує тренувальний план на основі:
    - профілю користувача (поки що не чіпаємо)
    - результатів тестів (assessment)
    - типу програми
    - локації (дім/зал)
    """

    template = get_program_template(
        program_type, location, days_per_week=user.trainings_per_week
    )

    si = StrengthIndex(
        si_push=assessment.si_push,
        si_squat=assessment.si_squat,
        si_core=assessment.si_core,
    )

    plan_struct: Dict[str, Any] = {
        "program_type": template.program_type,
        "location": template.location,
        "days_per_week": template.days_per_week,
        "days": [],
    }

    for day in template.days:
        day_data = {
            "day_index": day.day_index,
            "name": day.name,
            "exercises": [],
        }

        for ex in day.exercises:
            if ex.muscle_group == "push":
                si_used = si.si_push
            elif ex.muscle_group == "legs":
                si_used = si.si_squat
            elif ex.muscle_group == "core":
                si_used = si.si_core
            else:
                si_used = 1.0

            base = ex

            sets = calc_sets(base.base_sets, si_used)
            reps = calc_reps(base.base_reps, si_used)
            rest = calc_rest(base.base_rest, si_used)

            day_data["exercises"].append(
                {
                    "name": base.name,
                    "muscle_group": base.muscle_group,
                    "type": base.type,
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

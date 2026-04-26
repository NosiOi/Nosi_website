from dataclasses import dataclass
from typing import List, Literal, Dict, Any

TrainingLocation = Literal["home", "gym"]
ProgramType = Literal["full_body"]  # потім додамо upper_lower, ppl і т.д.


@dataclass
class ExerciseVariant:
    name: str
    level: int  # 0 = найлегший, далі складніше
    muscle_group: str  # "push", "pull", "legs", "core"
    type: str  # "compound", "isolation", "bodyweight"
    base_sets: int
    base_reps: int
    base_rest: int  # сек


@dataclass
class TrainingDayTemplate:
    day_index: int
    name: str
    exercises: List[ExerciseVariant]


@dataclass
class ProgramTemplate:
    program_type: ProgramType
    location: TrainingLocation
    days_per_week: int
    days: List[TrainingDayTemplate]


# ВАРІАНТИ ВІДЖИМАНЬ
PUSH_EXERCISES_HOME: List[ExerciseVariant] = [
    ExerciseVariant(
        name="Віджимання від стіни",
        level=0,
        muscle_group="push",
        type="bodyweight",
        base_sets=3,
        base_reps=10,
        base_rest=60,
    ),
    ExerciseVariant(
        name="Віджимання від лавки",
        level=1,
        muscle_group="push",
        type="bodyweight",
        base_sets=3,
        base_reps=10,
        base_rest=60,
    ),
    ExerciseVariant(
        name="Класичні віджимання",
        level=2,
        muscle_group="push",
        type="bodyweight",
        base_sets=3,
        base_reps=10,
        base_rest=90,
    ),
    ExerciseVariant(
        name="Віджимання з вузькою постановкою рук",
        level=3,
        muscle_group="push",
        type="bodyweight",
        base_sets=3,
        base_reps=8,
        base_rest=90,
    ),
    ExerciseVariant(
        name="Віджимання з підвищенням ніг",
        level=4,
        muscle_group="push",
        type="bodyweight",
        base_sets=4,
        base_reps=8,
        base_rest=90,
    ),
]


# НОГИ
SQUAT_EXERCISES_HOME: List[ExerciseVariant] = [
    ExerciseVariant(
        name="Присідання з вагою тіла",
        level=0,
        muscle_group="legs",
        type="bodyweight",
        base_sets=3,
        base_reps=12,
        base_rest=60,
    ),
    ExerciseVariant(
        name="Присідання з паузою внизу",
        level=1,
        muscle_group="legs",
        type="bodyweight",
        base_sets=3,
        base_reps=10,
        base_rest=75,
    ),
    ExerciseVariant(
        name="Болгарські присідання",
        level=2,
        muscle_group="legs",
        type="bodyweight",
        base_sets=3,
        base_reps=8,
        base_rest=90,
    ),
    ExerciseVariant(
        name="Випади вперед",
        level=3,
        muscle_group="legs",
        type="bodyweight",
        base_sets=3,
        base_reps=10,
        base_rest=90,
    ),
]


# КОР
CORE_EXERCISES_HOME: List[ExerciseVariant] = [
    ExerciseVariant(
        name="Планка",
        level=0,
        muscle_group="core",
        type="bodyweight",
        base_sets=3,
        base_reps=30,  # секунди
        base_rest=45,
    ),
    ExerciseVariant(
        name="Планка з підйомом ноги",
        level=1,
        muscle_group="core",
        type="bodyweight",
        base_sets=3,
        base_reps=25,
        base_rest=45,
    ),
    ExerciseVariant(
        name="Скручування",
        level=2,
        muscle_group="core",
        type="bodyweight",
        base_sets=3,
        base_reps=15,
        base_rest=45,
    ),
]


def get_full_body_home_3_days_template() -> ProgramTemplate:
    day1 = TrainingDayTemplate(
        day_index=1,
        name="Full Body A",
        exercises=[
            SQUAT_EXERCISES_HOME[0],  # базові присідання
            PUSH_EXERCISES_HOME[2],  # класичні віджимання
            CORE_EXERCISES_HOME[0],  # планка
        ],
    )

    day2 = TrainingDayTemplate(
        day_index=2,
        name="Full Body B",
        exercises=[
            SQUAT_EXERCISES_HOME[1],  # присідання з паузою
            PUSH_EXERCISES_HOME[1],  # віджимання від лавки
            CORE_EXERCISES_HOME[2],  # скручування
        ],
    )

    day3 = TrainingDayTemplate(
        day_index=3,
        name="Full Body C",
        exercises=[
            SQUAT_EXERCISES_HOME[2],  # болгарські
            PUSH_EXERCISES_HOME[3],  # вузькі віджимання
            CORE_EXERCISES_HOME[1],  # планка з підйомом ноги
        ],
    )

    return ProgramTemplate(
        program_type="full_body",
        location="home",
        days_per_week=3,
        days=[day1, day2, day3],
    )


def get_program_template(
    program_type: ProgramType, location: TrainingLocation, days_per_week: int
) -> ProgramTemplate:
    # поки що тільки один варіант
    if program_type == "full_body" and location == "home" and days_per_week == 3:
        return get_full_body_home_3_days_template()
    # тут потім додаватимеш інші
    raise ValueError("Наразі такий тип програми ще не реалізований")

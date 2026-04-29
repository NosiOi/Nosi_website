from typing import List, Dict, Optional

EXERCISES_DB = {
    "chest": {
        "home": [
            "Віджимання",
            "Віджимання з вузькою постановкою рук",
            "Віджимання з піднятими ногами",
        ],
        "outdoor": [
            "Віджимання на брусах",
            "Віджимання від лавки",
            "Віджимання з широкою постановкою рук",
        ],
        "gym": ["Жим лежачи", "Жим на похилій лаві", "Жим гантелей лежачи"],
    },
    "back": {
        "home": ["Тяга еспандера до поясу", "Супермен", "Гіперекстензія без обтяження"],
        "outdoor": [
            "Підтягування",
            "Горизонтальні підтягування",
            "Тяга до поясу на турніку",
        ],
        "gym": ["Тяга штанги в нахилі", "Тяга верхнього блока", "Тяга Т-грифа"],
    },
    "shoulders": {
        "home": [
            "Віджимання в стійці біля стіни",
            "Підйоми рук в сторони з еспандером",
            "Підйоми рук вперед",
        ],
        "outdoor": [
            "Жим штанги стоячи (якщо є)",
            "Підйоми гантелей в сторони",
            "Підйоми гантелей вперед",
        ],
        "gym": [
            "Жим штанги стоячи",
            "Жим гантелей сидячи",
            "Розведення гантелей в сторони",
        ],
    },
    "biceps": {
        "home": [
            "Згинання рук з еспандером",
            "Згинання рук з рюкзаком",
            "Ізометричні утримання",
        ],
        "outdoor": [
            "Підтягування з вузьким хватом",
            "Згинання рук з гантелями",
            "Молоткові згинання",
        ],
        "gym": [
            "Згинання штанги стоячи",
            "Згинання гантелей сидячи",
            "Згинання на лаві Скотта",
        ],
    },
    "triceps": {
        "home": [
            "Віджимання з вузькою постановкою рук",
            "Віджимання від стільця",
            "Французькі віджимання",
        ],
        "outdoor": [
            "Віджимання на брусах",
            "Розгинання рук з гантеллю за головою",
            "Жим вузьким хватом",
        ],
        "gym": ["Французький жим", "Жим вузьким хватом", "Розгинання рук на блоці"],
    },
    "forearms": {
        "home": [
            "Вис на турніку (якщо є)",
            "Стискання еспандера",
            "Утримання ваги в руках",
        ],
        "outdoor": [
            "Вис на турніку",
            "Фермерська хода",
            "Підйоми на зап’ястя з гантелями",
        ],
        "gym": [
            "Згинання зап’ясть зі штангою",
            "Розгинання зап’ясть",
            "Фермерська хода з гантелями",
        ],
    },
    "neck": {
        "home": [
            "Ізометричні натискання головою в долоню",
            "Нахили голови з опором",
            "Повороти голови з опором",
        ],
        "outdoor": ["Ізометричні вправи на шию", "Нахили голови", "Повороти голови"],
        "gym": [
            "Тренажер для шиї",
            "Нахили голови з обтяженням",
            "Повороти голови з обтяженням",
        ],
    },
    "core": {
        "home": ["Планка", "Скручування", "Велосипед"],
        "outdoor": ["Планка", "Підйоми ніг у висі", "Скручування на лавці"],
        "gym": ["Планка", "Скручування на тренажері", "Підйоми ніг у висі"],
    },
    "lower_back": {
        "home": ["Супермен", "Гіперекстензія без обтяження", "Нахили вперед"],
        "outdoor": ["Гіперекстензія на лавці", "Супермен", "Нахили з обтяженням"],
        "gym": ["Гіперекстензія", "Станова тяга з малою вагою", "Добрі ранки"],
    },
    "quads": {
        "home": ["Присідання", "Випади", "Болгарські присідання"],
        "outdoor": ["Присідання", "Випади ходьбою", "Стрибки на тумбу"],
        "gym": ["Присідання зі штангою", "Жим ногами", "Випади зі штангою"],
    },
    "hamstrings": {
        "home": ["Румунська тяга з рюкзаком", "Місток", "Добрі ранки без ваги"],
        "outdoor": [
            "Румунська тяга з гантелями",
            "Місток",
            "Нордичні згинання (якщо можливо)",
        ],
        "gym": [
            "Румунська тяга",
            "Згинання ніг лежачи",
            "Гіперекстензія з акцентом на задню поверхню",
        ],
    },
    "glutes": {
        "home": ["Ягодичний міст", "Болгарські присідання", "Випади"],
        "outdoor": ["Ягодичний міст", "Випади ходьбою", "Стрибки на тумбу"],
        "gym": [
            "Ягодичний міст зі штангою",
            "Присідання",
            "Жим ногами з акцентом на сідниці",
        ],
    },
    "calves": {
        "home": [
            "Підйоми на носки стоячи",
            "Підйоми на носки на сходинці",
            "Підйоми на одній нозі",
        ],
        "outdoor": ["Підйоми на носки", "Стрибки на місці", "Біг на носках"],
        "gym": [
            "Підйоми на носки стоячи",
            "Підйоми на носки сидячи",
            "Підйоми на носки в тренажері",
        ],
    },
    "adductors": {
        "home": ["Пліє-присідання", "Слайди ногами в сторони", "Статичні розтяжки"],
        "outdoor": ["Пліє-присідання", "Бічні випади", "Розтяжка привідних"],
        "gym": [
            "Тренажер для зведення ніг",
            "Пліє-присідання зі штангою",
            "Бічні випади з гантелями",
        ],
    },
}

CRITICAL_WEAK = {"core", "lower_back"}


def _rep_scheme(goal: str):
    if goal == "gain":
        return 4, "6-12"
    if goal == "lose":
        return 3, "12-20"
    if goal == "maintain":
        return 3, "8-12"
    return 3, "8-12"


def _choose_split(workouts_per_week: int) -> str:
    if workouts_per_week <= 1:
        return "full_body_1"
    if workouts_per_week == 2:
        return "full_body_2"
    if workouts_per_week == 3:
        return "full_body_3"
    if workouts_per_week == 4:
        return "upper_lower"
    if workouts_per_week == 5:
        return "ppl_ul"
    if workouts_per_week == 6:
        return "ppl_x2"
    return "ppl_plus_core"


def _base_muscle_distribution(split: str) -> Dict[str, List[str]]:
    if split == "full_body_1":
        return {"day1": ["chest", "back", "quads", "core"]}
    if split == "full_body_2":
        return {
            "day1": ["chest", "back", "quads"],
            "day2": ["shoulders", "hamstrings", "core"],
        }
    if split == "full_body_3":
        return {
            "day1": ["chest", "back", "core"],
            "day2": ["legs", "glutes", "calves"],
            "day3": ["shoulders", "arms", "core"],
        }
    if split == "upper_lower":
        return {
            "day1": ["chest", "back", "shoulders", "arms", "core"],
            "day2": ["quads", "hamstrings", "glutes", "calves", "core"],
            "day3": ["chest", "back", "shoulders", "arms"],
            "day4": ["legs", "glutes", "core"],
        }
    if split == "ppl_ul":
        return {
            "day1": ["chest", "shoulders", "triceps"],
            "day2": ["back", "biceps", "core"],
            "day3": ["quads", "hamstrings", "glutes", "calves"],
            "day4": ["chest", "back", "shoulders"],
            "day5": ["legs", "core"],
        }
    if split == "ppl_x2":
        return {
            "day1": ["chest", "shoulders", "triceps"],
            "day2": ["back", "biceps", "core"],
            "day3": ["quads", "hamstrings", "glutes", "calves"],
            "day4": ["chest", "shoulders", "triceps"],
            "day5": ["back", "biceps", "core"],
            "day6": ["legs", "core"],
        }
    return {
        "day1": ["chest", "shoulders", "triceps"],
        "day2": ["back", "biceps", "core"],
        "day3": ["legs", "glutes", "calves"],
        "day4": ["chest", "back", "core"],
        "day5": ["legs", "core"],
        "day6": ["mobility"],
        "day7": ["core", "mobility"],
    }


def _normalize_env(env: Optional[str]) -> str:
    if env in ("home", "outdoor", "gym"):
        return env
    return "gym"


def _pick_exercises_for_muscle(muscle: str, env: str) -> List[str]:
    if muscle == "legs":
        muscles = ["quads", "hamstrings", "glutes", "calves"]
        result = []
        for m in muscles:
            if m in EXERCISES_DB:
                result.extend(EXERCISES_DB[m][env][:1])
        return result
    if muscle == "arms":
        muscles = ["biceps", "triceps", "forearms"]
        result = []
        for m in muscles:
            if m in EXERCISES_DB:
                result.extend(EXERCISES_DB[m][env][:1])
        return result
    if muscle == "mobility":
        return ["Динамічна розминка", "Розтяжка стегон", "Розтяжка грудних м’язів"]
    if muscle in EXERCISES_DB:
        return EXERCISES_DB[muscle][_normalize_env(env)][:3]
    return []


def _analyze_recommendations(
    aesthetic_focus: Optional[str],
    performance_focus: Optional[str],
    weak_points: Optional[List[str]],
    strong_points: Optional[List[str]],
) -> List[str]:
    weak_points = weak_points or []
    strong_points = strong_points or []
    recs = []

    if aesthetic_focus and aesthetic_focus in strong_points:
        recs.append(
            f"Обрана естетична ціль ({aesthetic_focus}) вже є сильною стороною. Можливо, варто збалансувати інші групи."
        )

    critical_weak = CRITICAL_WEAK.intersection(set(weak_points))
    if critical_weak:
        recs.append(
            "Виявлено критично слабкі зони: "
            + ", ".join(critical_weak)
            + ". Рекомендується приділити їм додаткову увагу."
        )

    if performance_focus == "pushups" and "chest" in strong_points:
        recs.append(
            "Ти хочеш збільшити кількість віджимань, але груди вже сильні. Ми додамо акцент на кор і стабілізацію."
        )

    return recs


def generate_training_plan(
    experience: str,
    workouts_per_week: int,
    goal: str,
    aesthetic_focus: Optional[str] = None,
    performance_focus: Optional[str] = None,
    environment: Optional[str] = "gym",
    weak_points: Optional[List[str]] = None,
    strong_points: Optional[List[str]] = None,
) -> Dict:
    workouts_per_week = max(1, min(int(workouts_per_week), 7))
    split = _choose_split(workouts_per_week)
    distribution = _base_muscle_distribution(split)
    sets, reps = _rep_scheme(goal)

    weak_points = weak_points or []
    strong_points = strong_points or []

    plan = {}
    for day, muscles in distribution.items():
        day_exercises = []

        for muscle in muscles:
            ex_list = _pick_exercises_for_muscle(muscle, environment)
            for ex in ex_list:
                day_exercises.append(
                    {
                        "exercise": ex,
                        "muscle_group": muscle,
                        "sets": sets,
                        "reps": reps,
                    }
                )

        if aesthetic_focus and aesthetic_focus in EXERCISES_DB:
            extra = _pick_exercises_for_muscle(aesthetic_focus, environment)
            for ex in extra[:1]:
                day_exercises.append(
                    {
                        "exercise": ex,
                        "muscle_group": aesthetic_focus,
                        "sets": sets,
                        "reps": reps,
                    }
                )

        if "core" in weak_points and "core" not in muscles:
            core_ex = _pick_exercises_for_muscle("core", environment)
            if core_ex:
                day_exercises.append(
                    {
                        "exercise": core_ex[0],
                        "muscle_group": "core",
                        "sets": 3,
                        "reps": "30-45 сек" if "Планка" in core_ex[0] else "12-15",
                    }
                )

        plan[day] = day_exercises

    recommendations = _analyze_recommendations(
        aesthetic_focus, performance_focus, weak_points, strong_points
    )

    return {
        "days": plan,
        "recommendations": recommendations,
        "meta": {
            "experience": experience,
            "workouts_per_week": workouts_per_week,
            "goal": goal,
            "aesthetic_focus": aesthetic_focus,
            "performance_focus": performance_focus,
            "environment": _normalize_env(environment),
        },
    }

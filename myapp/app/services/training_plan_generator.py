def generate_training_plan(experience: str, workouts_per_week: int, goal: str):
    workouts_per_week = int(workouts_per_week)

    frequency = min(workouts_per_week, 5)

    if experience == "beginner":
        base_exercises = ["Присідання", "Жим лежачи", "Тяга верхнього блока", "Планка"]
    elif experience == "intermediate":
        base_exercises = [
            "Присідання зі штангою",
            "Жим лежачи",
            "Тяга штанги в нахилі",
            "Румунська тяга",
        ]
    else:
        base_exercises = [
            "Фронтальні присідання",
            "Жим на похилій",
            "Тяга Т-грифа",
            "Станова тяга",
        ]

    plan = []
    for i in range(frequency):
        plan.append({"day": i + 1, "exercises": base_exercises})

    return plan

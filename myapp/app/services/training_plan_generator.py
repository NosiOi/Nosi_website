def generate_training_plan(goal, experience, workouts_per_week):
    if experience == "beginner":
        frequency = min(workouts_per_week, 3)
        plan_type = "full_body"
    elif experience == "intermediate":
        frequency = min(workouts_per_week, 4)
        plan_type = "upper_lower"
    else:
        frequency = min(workouts_per_week, 5)
        plan_type = "split"

    workout_structure = {
        "warmup": "5–10 хвилин кардіо + мобільність",
        "main": "40–50 хвилин силових вправ",
        "cooldown": "5–10 хвилин розтяжки",
    }

    return {"frequency": frequency, "type": plan_type, "structure": workout_structure}

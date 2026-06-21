from typing import Dict, List


class PlanSplitLogic:

    @staticmethod
    def choose_split(workouts_per_week: int) -> str:
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
        return "hybrid"

    @staticmethod
    def base_distribution(split: str) -> Dict[str, List[str]]:
        splits = {
            "full_body_1": {"day1": ["chest", "back", "legs", "core"]},
            "full_body_2": {
                "day1": ["chest", "back", "legs"],
                "day2": ["shoulders", "arms", "core"]
            },
            "full_body_3": {
                "day1": ["chest", "back", "core"],
                "day2": ["legs", "glutes", "calves"],
                "day3": ["shoulders", "arms", "core"]
            },
            "upper_lower": {
                "day1": ["chest", "back", "shoulders", "arms"],
                "day2": ["legs", "glutes", "calves", "core"],
                "day3": ["chest", "back", "shoulders"],
                "day4": ["legs", "glutes", "core"]
            },
            "ppl_ul": {
                "day1": ["chest", "shoulders", "triceps"],
                "day2": ["back", "biceps", "core"],
                "day3": ["legs", "glutes", "calves"],
                "day4": ["chest", "back", "shoulders"],
                "day5": ["legs", "core"]
            },
            "ppl_x2": {
                "day1": ["chest", "shoulders", "triceps"],
                "day2": ["back", "biceps", "core"],
                "day3": ["legs", "glutes", "calves"],
                "day4": ["chest", "shoulders", "triceps"],
                "day5": ["back", "biceps", "core"],
                "day6": ["legs", "core"]
            },
            "hybrid": {
                "day1": ["chest", "back", "core"],
                "day2": ["legs", "glutes", "calves"],
                "day3": ["shoulders", "arms"],
                "day4": ["core", "mobility"],
                "day5": ["legs", "core"],
                "day6": ["push", "pull"],
                "day7": ["mobility"]
            }
        }
        return splits.get(split, splits["full_body_1"])

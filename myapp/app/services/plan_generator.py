from .sleep_calculator import calculate_sleep
from .calories_calculator import calculate_bmr, calculate_tdee, calculate_calories_goal
from .macros_calculator import calculate_macros
from .water_calculator import calculate_water
from .training_plan_generator import generate_training_plan


class PlanGenerator:
    def __init__(
        self, age, gender, weight, height, activity, goal, experience, workouts_per_week
    ):
        self.age = age
        self.gender = gender
        self.weight = weight
        self.height = height
        self.activity = activity
        self.goal = goal
        self.experience = experience
        self.workouts_per_week = workouts_per_week

    def generate(self):
        sleep = calculate_sleep(self.age)
        bmr = calculate_bmr(self.weight, self.height, self.age, self.gender)
        tdee = calculate_tdee(bmr, self.activity)
        calories = calculate_calories_goal(tdee, self.goal)
        macros = calculate_macros(self.weight, calories, self.goal)
        water = calculate_water(self.weight)
        training = generate_training_plan(
            self.goal, self.experience, self.workouts_per_week
        )

        return {
            "sleep": sleep,
            "calories": round(calories),
            "macros": macros,
            "water_liters": water,
            "training": training,
        }

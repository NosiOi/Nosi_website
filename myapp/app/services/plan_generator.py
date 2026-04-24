from .sleep_calculator import calculate_sleep
from .calories_calculator import calculate_calories_goal
from .macros_calculator import calculate_macros
from .water_calculator import calculate_water
from .training_plan_generator import generate_training_plan

print("LOADED FROM:", __file__)


class PlanGenerator:
    def __init__(
        self,
        age: int,
        sex: str,
        weight: float,
        height: float,
        activity: float,
        goal: str,
        experience: str,
        workouts_per_week: int,
    ):
        self.age = int(age)
        self.sex = sex
        self.weight = float(weight)
        self.height = float(height)
        self.activity = float(activity)
        self.goal = goal
        self.experience = experience
        self.workouts_per_week = int(workouts_per_week)

    def calculate_sleep(self):
        sleep = calculate_sleep(self.age)

        if isinstance(sleep, (tuple, list)):
            sleep = sum(sleep) / len(sleep)

        return int(round(float(sleep)))

    def calculate_calories(self):
        if self.sex == "male":
            bmr = 10 * self.weight + 6.25 * self.height - 5 * self.age + 5
        else:
            bmr = 10 * self.weight + 6.25 * self.height - 5 * self.age - 161

        tdee = bmr * self.activity
        calories = calculate_calories_goal(tdee, self.goal)
        return round(calories)

    def calculate_macros(self):
        calories = self.calculate_calories()
        macros = calculate_macros(self.weight, calories, self.goal)
        return {
            "protein": round(macros["protein"]),
            "fats": round(macros["fat"]),
            "carbs": round(macros["carbs"]),
        }

    def calculate_water(self):
        return round(float(calculate_water(self.weight, self.activity)), 2)

    def calculate_training_plan(self):
        return generate_training_plan(
            experience=self.experience,
            workouts_per_week=self.workouts_per_week,
            goal=self.goal,
        )

    def generate(self):
        macros = self.calculate_macros()

        return {
            "sleep": self.calculate_sleep(),
            "calories": self.calculate_calories(),
            "protein": macros["protein"],
            "fats": macros["fats"],
            "carbs": macros["carbs"],
            "water": self.calculate_water(),
            "training_plan": self.calculate_training_plan(),
        }

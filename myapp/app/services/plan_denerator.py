class PlanGenerator:
    def __init__(
        self, age, sex, weight, height, activity, goal, experience, workouts_per_week
    ): ...

    def calculate_sleep(self): ...

    def calculate_calories(self): ...

    def calculate_macros(self): ...

    def calculate_water(self): ...

    def calculate_training_plan(self): ...

    def generate(self):
        return {
            "sleep": self.calculate_sleep(),
            "calories": self.calculate_calories(),
            "macros": self.calculate_macros(),
            "water": self.calculate_water(),
            "training": self.calculate_training_plan(),
        }

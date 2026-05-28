import requests

API_KEY = "YOUR_USDA_API_KEY"

def fetch_food_data(query):
    search_url = f"https://api.nal.usda.gov/fdc/v1/foods/search?api_key={API_KEY}"
    response = requests.post(search_url, json={"query": query})

    data = response.json()

    if not data["foods"]:
        return default_values()

    food = data["foods"][0]

    nutrients = {n["nutrientName"]: n["value"] for n in food["foodNutrients"]}

    return {
        "calories": nutrients.get("Energy", 0),
        "protein": nutrients.get("Protein", 0),
        "fat": nutrients.get("Total lipid (fat)", 0),
        "carbs": nutrients.get("Carbohydrate, by difference", 0),
        "fiber": nutrients.get("Fiber, total dietary", 0),
        "category": food.get("foodCategory", "unknown")
    }


def default_values():
    return {
        "calories": 0,
        "protein": 0,
        "fat": 0,
        "carbs": 0,
        "fiber": 0,
        "category": "unknown"
    }

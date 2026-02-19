from fastmcp import FastMCP

mcp = FastMCP("Nutrition Database")


@mcp.tool
def get_calories(food: str, grams: int) -> str:
    data = {"chicken": 165, "rice": 130, "broccoli": 34, "oats": 389, "egg": 155}
    kcal_per_100 = data.get(food.lower(), 100)
    kcal = grams * kcal_per_100 / 100
    return f"{food}: {kcal:.1f} kcal for {grams}g"


@mcp.tool
def suggest_meal_split(goal: str, weight: float) -> str:
    protein = weight * 1.8
    carbs = weight * 3.0
    fats = weight * 0.8
    return (
        f"Goal={goal}; daily targets: protein={protein:.0f}g, "
        f"carbs={carbs:.0f}g, fats={fats:.0f}g split across 4 meals."
    )


if __name__ == "__main__":
    mcp.run()

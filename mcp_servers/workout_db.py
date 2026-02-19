from fastmcp import FastMCP

mcp = FastMCP("Workout Database")


@mcp.tool
def get_exercises(muscle_group: str) -> str:
    exercises = {
        "chest": "Bench Press, Incline Press, Cable Fly",
        "legs": "Squats, Romanian Deadlift, Walking Lunges",
        "back": "Pullups, Barbell Row, Lat Pulldown",
        "shoulders": "Overhead Press, Lateral Raise, Rear Delt Fly",
    }
    return exercises.get(muscle_group.lower(), "No exercises found")


@mcp.tool
def build_split(goal: str) -> str:
    if "muscle" in goal.lower():
        return "Push/Pull/Legs split repeated over 6 training days."
    return "Upper/Lower split 4 days per week."


if __name__ == "__main__":
    mcp.run()

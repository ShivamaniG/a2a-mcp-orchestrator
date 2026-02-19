from fastmcp import FastMCP

mcp = FastMCP("Progress Tracker")


@mcp.tool
def estimate_progress(goal: str, weeks: int, weight: float) -> str:
    return (
        f"For goal '{goal}', expect measurable cardio improvements within {weeks} weeks "
        f"at current weight {weight:.1f}kg with 3 sessions/week."
    )


@mcp.tool
def adjust_plan(fatigue_level: str) -> str:
    fatigue = fatigue_level.lower()
    if fatigue == "high":
        return "Reduce interval intensity by 20% and add one rest day."
    if fatigue == "moderate":
        return "Keep volume, reduce tempo intensity for one session."
    return "Progress as planned."


if __name__ == "__main__":
    mcp.run()

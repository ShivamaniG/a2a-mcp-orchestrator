import os
from typing import Any, Dict

from agents.common import MCPToolClient, call_collaborator, discover_collaborator_card

mcp_client = MCPToolClient()


async def init_tools():
    script = os.path.join(os.path.dirname(__file__), "..", "..", "mcp_servers", "workout_db.py")
    await mcp_client.connect("workout_db", script)


async def close_tools():
    await mcp_client.close()


async def build_muscle_plan(query: str, weight: float, context: Dict[str, Any]) -> Dict[str, Any]:
    exercises = await mcp_client.call(
        "workout_db",
        "get_exercises",
        {"muscle_group": "legs"},
    )
    split = await mcp_client.call(
        "workout_db",
        "build_split",
        {"goal": query},
    )
    plan: Dict[str, Any] = {
        "strength_focus": exercises,
        "weekly_split": split,
        "progressive_overload": "Increase load by 2.5-5% weekly if reps are completed cleanly.",
        "weight_reference_kg": weight,
    }

    skip_collab = bool(context.get("skip_collab"))
    if not skip_collab:
        diet_card = await discover_collaborator_card("nutrition", exclude_name="muscle_agent")
        if diet_card:
            diet_plan = await call_collaborator(
                diet_card["url"],
                {"query": "high protein meals for muscle gain", "weight": weight, "context": {"skip_collab": True}},
                diet_card.get("query_endpoint", "/query"),
            )
            plan["diet_support"] = diet_plan.get("plan", {})

    return plan

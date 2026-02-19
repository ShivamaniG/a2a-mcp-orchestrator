import os
from typing import Any, Dict

from agents.common import MCPToolClient, call_collaborator, discover_collaborator_card

mcp_client = MCPToolClient()


async def init_tools():
    script = os.path.join(os.path.dirname(__file__), "..", "..", "mcp_servers", "nutrition_db.py")
    await mcp_client.connect("nutrition_db", script)


async def close_tools():
    await mcp_client.close()


async def build_diet_plan(query: str, weight: float, context: Dict[str, Any]) -> Dict[str, Any]:
    protein_grams = int(weight * 1.8)
    chicken_kcal = await mcp_client.call(
        "nutrition_db", "get_calories", {"food": "chicken", "grams": 200}
    )
    rice_kcal = await mcp_client.call(
        "nutrition_db", "get_calories", {"food": "rice", "grams": 250}
    )
    split = await mcp_client.call(
        "nutrition_db",
        "suggest_meal_split",
        {"goal": query, "weight": weight},
    )

    plan: Dict[str, Any] = {
        "target_protein_g": protein_grams,
        "sample_meals": [chicken_kcal, rice_kcal],
        "meal_split": split,
    }

    skip_collab = bool(context.get("skip_collab"))
    if not skip_collab:
        trainer_card = await discover_collaborator_card(
            "personal-training", exclude_name="diet_agent"
        )
        if trainer_card:
            suggestion = await call_collaborator(
                trainer_card["url"],
                {"query": "best meal timing around workouts", "weight": weight, "context": {"skip_collab": True}},
                trainer_card.get("query_endpoint", "/query"),
            )
            plan["trainer_note"] = suggestion.get("summary", "No trainer note")

    return plan

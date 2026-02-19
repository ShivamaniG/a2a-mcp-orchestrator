import os
from typing import Any, Dict

from agents.common import MCPToolClient, call_collaborator, discover_collaborator_card

mcp_client = MCPToolClient()


async def init_tools():
    script = os.path.join(
        os.path.dirname(__file__), "..", "..", "mcp_servers", "progress_tracker.py"
    )
    await mcp_client.connect("progress_tracker", script)


async def close_tools():
    await mcp_client.close()


async def build_cardio_plan(query: str, weight: float, context: Dict[str, Any]) -> Dict[str, Any]:
    estimate = await mcp_client.call(
        "progress_tracker",
        "estimate_progress",
        {"goal": query, "weeks": 8, "weight": weight},
    )
    adjustment = await mcp_client.call(
        "progress_tracker",
        "adjust_plan",
        {"fatigue_level": "moderate"},
    )
    plan: Dict[str, Any] = {
        "weekly_cardio": "3 sessions: intervals, zone2, long run",
        "progress_estimate": estimate,
        "adjustment_rule": adjustment,
    }

    skip_collab = bool(context.get("skip_collab"))
    if not skip_collab:
        muscle_card = await discover_collaborator_card(
            "strength-training", exclude_name="cardio_agent"
        )
        if muscle_card:
            base = await call_collaborator(
                muscle_card["url"],
                {"query": "strength base for runners", "weight": weight, "context": {"skip_collab": True}},
                muscle_card.get("query_endpoint", "/query"),
            )
            plan["strength_base"] = base.get("plan", {})

    return plan

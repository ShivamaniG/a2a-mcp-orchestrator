import asyncio
from typing import Any, Dict, Optional

from agents.common import call_collaborator, discover_collaborator_card


async def _call_if_available(card: Optional[Dict[str, Any]], payload: Dict[str, Any]):
    if not card:
        return {"summary": "Agent unavailable", "plan": {}, "source": "none"}
    return await call_collaborator(card["url"], payload, card.get("query_endpoint", "/query"))


async def personal_trainer_plan(goal: str, weight: float) -> Dict[str, Any]:
    muscle = await discover_collaborator_card("muscle-building", exclude_name="trainer_agent")
    cardio = await discover_collaborator_card("cardio-endurance", exclude_name="trainer_agent")
    diet = await discover_collaborator_card("nutrition", exclude_name="trainer_agent")

    payload_base = {"weight": weight, "context": {"skip_collab": True}}

    muscle_task = _call_if_available(
        muscle,
        {"query": f"muscle strategy for: {goal}", **payload_base},
    )
    cardio_task = _call_if_available(
        cardio,
        {"query": f"cardio strategy for: {goal}", **payload_base},
    )
    diet_task = _call_if_available(
        diet,
        {"query": f"diet strategy for: {goal}", **payload_base},
    )

    muscle_result, cardio_result, diet_result = await asyncio.gather(
        muscle_task, cardio_task, diet_task
    )

    return {
        "goal": goal,
        "weight_kg": weight,
        "trainer_schedule": "8-week blended block: 3 strength + 3 cardio + 7-day nutrition structure.",
        "muscle": muscle_result,
        "cardio": cardio_result,
        "diet": diet_result,
    }

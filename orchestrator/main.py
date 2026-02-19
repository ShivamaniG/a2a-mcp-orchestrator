import os
from typing import Any, Dict

import httpx
import uvicorn
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel

app = FastAPI(title="Fitness A2A Orchestrator")

REGISTRY_URL = os.getenv("REGISTRY_URL", "http://localhost:8000").rstrip("/")


class PlanRequest(BaseModel):
    goal: str
    weight: float = 70.0


async def discover_card(capability: str):
    async with httpx.AsyncClient(timeout=20.0) as client:
        resp = await client.get(f"{REGISTRY_URL}/cards", params={"capability": capability})
        resp.raise_for_status()
        cards = resp.json().get("cards", [])
    return cards[0] if cards else None


async def call_agent(agent_url: str, payload: Dict[str, Any], query_endpoint: str = "/query"):
    endpoint = query_endpoint if query_endpoint.startswith("/") else f"/{query_endpoint}"
    async with httpx.AsyncClient(timeout=45.0) as client:
        resp = await client.post(f"{agent_url.rstrip('/')}{endpoint}", json=payload)
        resp.raise_for_status()
        return resp.json()


@app.post("/plan")
async def create_plan(req: PlanRequest):
    trainer_card = await discover_card("personal-training")
    if not trainer_card:
        raise HTTPException(404, "No trainer agent found")

    payload = {"query": req.goal, "weight": req.weight, "context": {}}
    try:
        result = await call_agent(
            trainer_card["url"], payload, trainer_card.get("query_endpoint", "/query")
        )
        return {
            "orchestrator_used": "fitness_orchestrator",
            "trainer_agent": trainer_card["name"],
            "trainer_card_used": trainer_card,
            "tools_used": result.get("tools_used", []),
            "result": result,
        }
    except httpx.HTTPError as e:
        raise HTTPException(502, f"Agent call failed: {str(e)}")


@app.get("/health")
async def health():
    return {"status": "healthy"}


if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8001)

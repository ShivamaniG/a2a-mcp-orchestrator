from typing import Any, Dict

import uvicorn
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel, Field

from agents.common import deregister_self, register_self
from agents.trainer_agent.logic import personal_trainer_plan

AGENT_NAME = "trainer_agent"
AGENT_URL = "http://localhost:8005"
CAPABILITIES = ["personal-training", "fitness-coaching"]
AGENT_CARD = {
    "name": AGENT_NAME,
    "url": AGENT_URL,
    "version": "1.0.0",
    "description": "Coordinator agent that composes muscle, cardio, and diet plans.",
    "capabilities": CAPABILITIES,
    "mcp_tools": [],
    "input_schema": {"query": "str", "weight": "float", "context": "dict"},
    "output_schema": {
        "summary": "str",
        "plan": "dict",
        "source": "str",
        "tools_used": "list[str]",
    },
    "query_endpoint": "/query",
    "health_endpoint": "/health",
    "collaborates_with": ["muscle_agent", "cardio_agent", "diet_agent"],
}

app = FastAPI(title="Trainer Agent")


class QueryRequest(BaseModel):
    query: str
    weight: float = 70.0
    context: Dict[str, Any] = Field(default_factory=dict)


@app.on_event("startup")
async def startup():
    await register_self(AGENT_NAME, AGENT_URL, CAPABILITIES, [], AGENT_CARD)


@app.on_event("shutdown")
async def shutdown():
    await deregister_self(AGENT_NAME)


@app.post("/query")
async def query(req: QueryRequest):
    try:
        plan = await personal_trainer_plan(req.query, req.weight)
        muscle_tools = plan.get("muscle", {}).get("tools_used", [])
        cardio_tools = plan.get("cardio", {}).get("tools_used", [])
        diet_tools = plan.get("diet", {}).get("tools_used", [])
        return {
            "summary": "Trainer plan synthesized from collaborator agents",
            "plan": plan,
            "source": "trainer_agent",
            "collaborators_used": ["muscle_agent", "cardio_agent", "diet_agent"],
            "tools_used": sorted(list(set(muscle_tools + cardio_tools + diet_tools))),
        }
    except Exception as e:
        raise HTTPException(500, str(e))


@app.get("/health")
async def health():
    return {"status": "healthy", "capabilities": CAPABILITIES}


@app.get("/agent-card")
async def agent_card():
    return AGENT_CARD


if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8005)

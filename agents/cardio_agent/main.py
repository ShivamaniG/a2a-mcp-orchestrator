from typing import Any, Dict

import uvicorn
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel, Field

from agents.cardio_agent.logic import build_cardio_plan, close_tools, init_tools
from agents.common import deregister_self, register_self

AGENT_NAME = "cardio_agent"
AGENT_URL = "http://localhost:8003"
CAPABILITIES = ["cardio-endurance", "running-plan"]
MCP_TOOLS = ["estimate_progress", "adjust_plan"]
AGENT_CARD = {
    "name": AGENT_NAME,
    "url": AGENT_URL,
    "version": "1.0.0",
    "description": "Builds cardio endurance plans and progression adjustments.",
    "capabilities": CAPABILITIES,
    "mcp_tools": MCP_TOOLS,
    "input_schema": {"query": "str", "weight": "float", "context": "dict"},
    "output_schema": {
        "summary": "str",
        "plan": "dict",
        "source": "str",
        "tools_used": "list[str]",
    },
    "query_endpoint": "/query",
    "health_endpoint": "/health",
    "collaborates_with": ["muscle_agent"],
}

app = FastAPI(title="Cardio Agent")


class QueryRequest(BaseModel):
    query: str
    weight: float = 70.0
    context: Dict[str, Any] = Field(default_factory=dict)


@app.on_event("startup")
async def startup():
    await init_tools()
    await register_self(AGENT_NAME, AGENT_URL, CAPABILITIES, MCP_TOOLS, AGENT_CARD)


@app.on_event("shutdown")
async def shutdown():
    await close_tools()
    await deregister_self(AGENT_NAME)


@app.post("/query")
async def query(req: QueryRequest):
    try:
        plan = await build_cardio_plan(req.query, req.weight, req.context)
        return {
            "summary": "Cardio plan generated",
            "plan": plan,
            "source": "cardio_agent",
            "collaborators_used": ["muscle_agent"] if "strength_base" in plan else [],
            "tools_used": ["estimate_progress", "adjust_plan"],
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
    uvicorn.run(app, host="0.0.0.0", port=8003)

import asyncio
import base64
from typing import Any, Dict, List, Optional

import httpx
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel

app = FastAPI(title="A2A Orchestrator + Registry")

registry: List[Dict[str, Any]] = []


class AgentRegistration(BaseModel):
    name: str
    url: str
    capabilities: List[str]
    mcp_tools: List[str] = []


class AgentDiscovery(BaseModel):
    agents: List[Dict[str, Any]]


class OrchestratorQueryRequest(BaseModel):
    query: str
    base64_pdf: Optional[str] = None


@app.post("/register")
async def register(agent: AgentRegistration):
    global registry
    registry = [a for a in registry if a["name"] != agent.name]

    agent_dict = agent.dict()
    agent_dict["status"] = "alive"
    registry.append(agent_dict)

    print(f"Registered: {agent.name} -> {agent.url}")
    return {"status": "registered", "name": agent.name}


@app.get("/discover", response_model=AgentDiscovery)
async def discover(capability: Optional[str] = None, name: Optional[str] = None):
    results = []
    for agent in registry:
        if agent.get("status") != "alive":
            continue

        if name and agent["name"] == name:
            results.append(agent)
        elif capability:
            if capability in agent["capabilities"] or capability in agent.get("mcp_tools", []):
                results.append(agent)
        else:
            results.append(agent)

    return AgentDiscovery(agents=results)


@app.get("/health")
async def health():
    alive = len([a for a in registry if a.get("status") == "alive"])
    return {"status": "healthy", "agents_alive": alive}


async def orchestrate_query(query: str, base64_pdf: Optional[str] = None):
    """Full orchestration flow."""
    print(f"\nUser Query: {query}")
    print("Step 1: Discover A2A agents...")

    disc = await discover(capability="pdf-summary")
    print(f"Found agents: {[a['name'] for a in disc.agents]}")

    if not disc.agents:
        raise HTTPException(404, "No suitable agents found")

    target_agent = disc.agents[0]
    agent_url = target_agent["url"]
    print(f"Step 2: Calling {target_agent['name']} at {agent_url}")

    async with httpx.AsyncClient(timeout=30.0) as client:
        resp = await client.post(
            f"{agent_url}/query",
            json={"query": query, "base64_pdf": base64_pdf},
        )
        resp.raise_for_status()
        result = resp.json()

    summary = result.get("summary", str(result))
    synthesis = (
        "ORCHESTRATOR SYNTHESIS:\n"
        f"- Used A2A Agent: {target_agent['name']}\n"
        f"- MCP Tools used: {target_agent.get('mcp_tools', [])}\n"
        f"- Result: {summary}"
    )
    return synthesis


@app.post("/query")
async def query(request: OrchestratorQueryRequest):
    try:
        result = await orchestrate_query(request.query, request.base64_pdf)
        return {"result": result}
    except HTTPException:
        raise
    except httpx.HTTPError as e:
        raise HTTPException(502, f"Agent call failed: {str(e)}")
    except Exception as e:
        raise HTTPException(500, f"Orchestration failed: {str(e)}")


if __name__ == "__main__":
    demo_pdf_b64 = base64.b64encode(
        b"%PDF-1.4\n1 0 obj\n<< /Type /Catalog /Pages 2 0 R >>\nendobj\n..."
    ).decode()

    print("Starting Orchestrator + Registry...")
    print("Run in separate terminals:")
    print("1. uvicorn orchestrator:app --port 8000")
    print("2. uvicorn hybrid_agent:app --port 8001")
    print("3. python mcp_server.py")
    print("\nThen test:")
    print("curl -X POST http://localhost:8000/query -H 'Content-Type: application/json' -d '{\"query\": \"Summarize this PDF\", \"base64_pdf\": \"...\"}'")

    loop = asyncio.get_event_loop()
    while True:
        user_query = input("\nQuery (or 'quit'): ")
        if user_query.lower() == "quit":
            break

        maybe_pdf = demo_pdf_b64 if "pdf" in user_query.lower() else None
        output = loop.run_until_complete(orchestrate_query(user_query, maybe_pdf))
        print(output)

from typing import List, Optional

from fastapi import FastAPI, HTTPException

from registry.models import (
    AgentDeregistration,
    AgentCard,
    AgentInfo,
    AgentRegistration,
    CardDiscoverResponse,
    DiscoverResponse,
)

app = FastAPI(title="A2A Registry")

registry: List[AgentInfo] = []


@app.post("/register")
async def register(agent: AgentRegistration):
    global registry
    registry = [a for a in registry if a.name != agent.name]
    registry.append(
        AgentInfo(
            name=agent.name,
            url=agent.url.rstrip("/"),
            capabilities=agent.capabilities,
            mcp_tools=agent.mcp_tools,
            metadata=agent.metadata,
            status="alive",
            agent_card=agent.agent_card,
        )
    )
    return {"status": "registered", "name": agent.name}


@app.post("/deregister")
async def deregister(payload: AgentDeregistration):
    global registry
    before = len(registry)
    registry = [a for a in registry if a.name != payload.name]
    removed = before - len(registry)
    if removed:
        return {"status": "removed", "name": payload.name}
    return {"status": "not_found", "name": payload.name}


@app.get("/discover", response_model=DiscoverResponse)
async def discover(capability: Optional[str] = None, name: Optional[str] = None):
    matches: List[AgentInfo] = []
    for agent in registry:
        if agent.status != "alive":
            continue
        if name and agent.name != name:
            continue
        if capability and capability not in agent.capabilities and capability not in agent.mcp_tools:
            continue
        matches.append(agent)
    return DiscoverResponse(agents=matches)


@app.get("/agents", response_model=DiscoverResponse)
async def agents():
    return DiscoverResponse(agents=[a for a in registry if a.status == "alive"])


@app.get("/cards", response_model=CardDiscoverResponse)
async def cards(capability: Optional[str] = None, name: Optional[str] = None):
    matches: List[AgentCard] = []
    for agent in registry:
        if agent.status != "alive" or agent.agent_card is None:
            continue
        card = agent.agent_card
        if name and card.name != name:
            continue
        if capability and capability not in card.capabilities and capability not in card.mcp_tools:
            continue
        matches.append(card)
    return CardDiscoverResponse(cards=matches)


@app.get("/agent-card/{name}", response_model=AgentCard)
async def agent_card(name: str):
    for agent in registry:
        if agent.status == "alive" and agent.name == name and agent.agent_card is not None:
            return agent.agent_card
    raise HTTPException(404, f"Agent card not found: {name}")


@app.get("/health")
async def health():
    alive = len([a for a in registry if a.status == "alive"])
    return {"status": "healthy", "agents_alive": alive}

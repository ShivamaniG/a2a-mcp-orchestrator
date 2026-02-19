import os
from contextlib import AsyncExitStack
from typing import Any, Dict, Optional

import httpx
from mcp import ClientSession
from mcp.client.stdio import StdioServerParameters, stdio_client


def registry_url() -> str:
    return os.getenv("REGISTRY_URL", "http://localhost:8000").rstrip("/")


class MCPToolClient:
    def __init__(self):
        self._stack = AsyncExitStack()
        self._sessions: Dict[str, ClientSession] = {}

    async def connect(self, name: str, script_path: str):
        if name in self._sessions:
            return
        params = StdioServerParameters(command="python", args=[os.path.abspath(script_path)])
        read, write = await self._stack.enter_async_context(stdio_client(params))
        session = await self._stack.enter_async_context(ClientSession(read, write))
        await session.initialize()
        self._sessions[name] = session

    async def call(self, server_name: str, tool_name: str, args: Dict[str, Any]) -> str:
        session = self._sessions[server_name]
        result = await session.call_tool(tool_name, args)
        return content_to_text(result)

    async def close(self):
        await self._stack.aclose()
        self._sessions = {}


def content_to_text(result: Any) -> str:
    content = getattr(result, "content", result)
    if isinstance(content, str):
        return content
    if isinstance(content, list):
        parts = []
        for item in content:
            text = getattr(item, "text", None)
            if text:
                parts.append(text)
            elif isinstance(item, dict) and "text" in item:
                parts.append(str(item["text"]))
            else:
                parts.append(str(item))
        return "\n".join(parts)
    return str(content)


async def register_self(
    name: str,
    url: str,
    capabilities: list[str],
    mcp_tools: Optional[list[str]] = None,
    agent_card: Optional[Dict[str, Any]] = None,
):
    payload = {
        "name": name,
        "url": url,
        "capabilities": capabilities,
        "mcp_tools": mcp_tools or [],
        "agent_card": agent_card,
    }
    async with httpx.AsyncClient(timeout=20.0) as client:
        resp = await client.post(f"{registry_url()}/register", json=payload)
        resp.raise_for_status()
        return resp.json()


async def deregister_self(name: str):
    async with httpx.AsyncClient(timeout=20.0) as client:
        resp = await client.post(f"{registry_url()}/deregister", json={"name": name})
        resp.raise_for_status()
        return resp.json()


async def discover_collaborator(capability: str, exclude_name: Optional[str] = None):
    async with httpx.AsyncClient(timeout=20.0) as client:
        resp = await client.get(f"{registry_url()}/discover", params={"capability": capability})
        resp.raise_for_status()
        agents = resp.json().get("agents", [])
    for agent in agents:
        if exclude_name and agent.get("name") == exclude_name:
            continue
        return agent
    return None


async def discover_collaborator_card(capability: str, exclude_name: Optional[str] = None):
    async with httpx.AsyncClient(timeout=20.0) as client:
        resp = await client.get(f"{registry_url()}/cards", params={"capability": capability})
        resp.raise_for_status()
        cards = resp.json().get("cards", [])
    for card in cards:
        if exclude_name and card.get("name") == exclude_name:
            continue
        return card
    return None


async def call_collaborator(
    agent_url: str, payload: Dict[str, Any], query_endpoint: str = "/query"
) -> Dict[str, Any]:
    endpoint = query_endpoint if query_endpoint.startswith("/") else f"/{query_endpoint}"
    async with httpx.AsyncClient(timeout=45.0) as client:
        resp = await client.post(f"{agent_url.rstrip('/')}{endpoint}", json=payload)
        resp.raise_for_status()
        return resp.json()

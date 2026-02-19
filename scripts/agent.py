import os
from contextlib import AsyncExitStack
from typing import Optional

import httpx
import uvicorn
from fastapi import FastAPI, HTTPException
from mcp import ClientSession
from mcp.client.stdio import StdioServerParameters, stdio_client
from pydantic import BaseModel

app = FastAPI(title="Summary Agent (A2A + MCP)")

mcp_session = None
_mcp_exit_stack = None


class QueryRequest(BaseModel):
    query: str
    base64_pdf: Optional[str] = None


class QueryResponse(BaseModel):
    summary: str
    source: str


REGISTRY_URL = "http://localhost:8000"


async def connect_mcp_pdf_tools():
    """Connect to MCP PDF server as a long-lived client session."""
    global mcp_session, _mcp_exit_stack
    if mcp_session is not None:
        return

    stack = AsyncExitStack()
    params = StdioServerParameters(
        command="python",
        args=[os.path.abspath("mcp_server.py")],
    )

    read, write = await stack.enter_async_context(stdio_client(params))
    session = await stack.enter_async_context(ClientSession(read, write))
    await session.initialize()
    tools = await session.list_tools()
    print(f"MCP tools loaded: {[t.name for t in tools.tools]}")

    mcp_session = session
    _mcp_exit_stack = stack


def _content_to_text(result) -> str:
    content = getattr(result, "content", result)
    if isinstance(content, str):
        return content
    if isinstance(content, list):
        parts = []
        for item in content:
            text = getattr(item, "text", None)
            if text:
                parts.append(text)
                continue
            if isinstance(item, dict) and "text" in item:
                parts.append(str(item["text"]))
                continue
            parts.append(str(item))
        return "\n".join(parts)
    return str(content)


@app.post("/query", response_model=QueryResponse)
async def handle_query(request: QueryRequest):
    global mcp_session

    if mcp_session is None:
        raise HTTPException(503, "MCP tools not ready")

    try:
        if request.base64_pdf:
            text_result = await mcp_session.call_tool(
                "extract_pdf_text",
                {"base64_pdf": request.base64_pdf},
            )
            pdf_text = _content_to_text(text_result)
            if pdf_text.startswith("Error:"):
                raise HTTPException(502, pdf_text)

            summary_result = await mcp_session.call_tool(
                "summarize_pdf",
                {"pdf_text": pdf_text},
            )
            return QueryResponse(
                summary=_content_to_text(summary_result),
                source="MCP PDF Tools + Summary Agent",
            )

        return QueryResponse(
            summary=f"Processed query: {request.query}",
            source="Summary Agent (no PDF)",
        )
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(500, f"MCP tool error: {str(e)}")


@app.get("/health")
async def health():
    return {"status": "healthy", "capabilities": ["pdf-summary", "text-summary"]}


@app.get("/capabilities")
async def capabilities():
    return {
        "name": "summary_agent",
        "capabilities": ["pdf-summary", "text-summary"],
        "mcp_tools": ["extract_pdf_text", "summarize_pdf"],
    }


async def register_self():
    async with httpx.AsyncClient() as client:
        resp = await client.post(
            f"{REGISTRY_URL}/register",
            json={
                "name": "summary_agent",
                "url": "http://localhost:8001",
                "capabilities": ["pdf-summary", "text-summary"],
                "mcp_tools": ["extract_pdf_text", "summarize_pdf"],
            },
        )
        resp.raise_for_status()
        print(f"Registered: {resp.json()}")


@app.on_event("startup")
async def startup():
    await connect_mcp_pdf_tools()
    await register_self()


@app.on_event("shutdown")
async def shutdown():
    global mcp_session, _mcp_exit_stack
    if _mcp_exit_stack is not None:
        await _mcp_exit_stack.aclose()
    mcp_session = None
    _mcp_exit_stack = None


if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8001)

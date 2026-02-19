# Multiagent Platform (A2A + MCP + Agent Cards)

This project shows how to build a multi-agent system where agents discover and call each other dynamically, use MCP tools for domain actions, and advertise capabilities through Agent Cards.

## How A2A is used

- `registry/` is the discovery layer.
- Each agent registers on startup (`/register`) and deregisters on shutdown (`/deregister`).
- Services discover collaborators by capability (`/discover` or `/cards`) instead of hardcoded peer URLs.
- `orchestrator/` receives user requests and routes them to the best coordinator agent (`trainer_agent` in this domain).

Result: any agent can call any other agent as long as capability matches.

## How MCP is used

- MCP servers live in `mcp_servers/` and expose tools (nutrition, workouts, progress).
- Domain agents connect to MCP servers via stdio using `MCPToolClient` in `agents/common.py`.
- Agents call `session.call_tool(...)` and include results in their plan output.

Result: tool execution is isolated from orchestration logic and can be swapped per domain.

## How Agent Cards are used

- Every agent exposes `GET /agent-card`.
- On startup, each agent registers its card in the registry (`agent_card` payload field).
- Orchestrator and trainer discover cards from `GET /cards` and call each agent through card metadata (`url`, `query_endpoint`, `capabilities`).

Result: routing is metadata-driven, not implementation-driven.

## Why this scales beyond fitness

This repo uses fitness agents (`muscle`, `cardio`, `diet`, `trainer`) only as an example.  
The same pattern works for any network/domain:

- Finance: risk, fraud, pricing, compliance agents
- Healthcare: triage, diagnostics, drug-check agents
- DevOps: incident, deployment, observability agents

To extend:

1. Add a new agent folder under `agents/`.
2. Give it capabilities + `agent-card`.
3. Register it to registry on startup.
4. Add/attach MCP tools if needed.
5. Existing orchestrator/trainer can discover and call it dynamically.

No architectural change is required to move from 4 agents to N agents.

## Runtime Docs

Startup commands, local run flow, and quick test commands are in `RUNNING.md`.

Here is a more compact and readable version with slightly reduced content but keeping the core meaning clear:

---

# A2A + MCP Orchestrator

This project demonstrates a scalable multi-agent architecture where agents dynamically discover and call each other, execute domain tools via MCP, and coordinate through a central orchestrator.

The system is capability-driven, not hardcoded. Any agent can collaborate with another as long as capabilities match.

---

## A2A (Agent-to-Agent Protocol, proposed by Google)

A2A enables dynamic discovery and communication between agents.

* `registry/` acts as the discovery backbone.
* Agents register on startup (`/register`) and deregister on shutdown (`/deregister`).
* Agents are discovered via `/discover` or `/cards` based on capabilities.
* No peer URLs are hardcoded; routing is metadata-driven.

### Agent Cards

Each agent exposes `GET /agent-card` and registers it with the registry.
The card contains:

* `url`
* `query_endpoint`
* `capabilities`
* optional metadata

The orchestrator and other agents fetch cards from `/cards` and route requests using capability matching.

Result: agents can call each other dynamically without tight coupling.

---

## MCP (Model Context Protocol, introduced by Anthropic)

MCP handles domain-specific tool execution.

* MCP servers live in `mcp_servers/`.
* Agents connect using `MCPToolClient`.
* Tools are executed via:

```
session.call_tool(...)
```

Tool execution is separated from orchestration, making domains easily replaceable.

---

## Orchestrator

The `orchestrator/` receives user requests and routes them to the appropriate coordinating agent.

In this example:

* Requests go to `trainer_agent`.
* The trainer discovers and invokes muscle, cardio, or diet agents based on capability.

The orchestrator manages routing only, not domain logic.

---

## Scalability

The fitness agents are examples. The same pattern applies to:

* Finance (risk, fraud, compliance)
* Healthcare (triage, diagnostics)
* DevOps (incident, deployment)

To extend:

1. Add a new agent under `agents/`
2. Define capabilities and expose `agent-card`
3. Register with the registry
4. Attach MCP tools if required

No architectural changes are needed to scale from a few agents to many.

---

## Runtime

Startup instructions and test commands are available in `RUNNING.md`.

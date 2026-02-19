# A2A + MCP Orchestrator

This project demonstrates how to build a scalable multi-agent system where agents dynamically discover and call each other, execute domain tools via MCP, and coordinate through a central orchestrator.

The architecture is capability-driven, not hardcoded. Any agent can collaborate with another as long as capabilities match.

---

## A2A (Agent-to-Agent Communication)

A2A enables agents to discover and communicate with each other dynamically.

### Discovery Layer

* The `registry/` service acts as the discovery backbone.
* Each agent registers itself on startup (`/register`) and deregisters on shutdown (`/deregister`).
* Agents are discovered based on capabilities using `/discover` or `/cards`.

There are no hardcoded peer URLs. Communication is entirely metadata-driven.

### Agent Cards (Part of A2A)

Agent Cards are the foundation of discoverability.

* Every agent exposes `GET /agent-card`.
* On startup, agents register their card with the registry.
* The card includes:

  * `url`
  * `query_endpoint`
  * `capabilities`
  * optional metadata

The orchestrator and other agents fetch cards using `GET /cards` and route requests based on capability matching.

Routing decisions are driven by metadata, not implementation details.

Result: Any agent can call any other agent dynamically as long as capability matches.

---

## MCP (Model Context Protocol)

MCP is responsible for domain-level tool execution.

* MCP servers live inside `mcp_servers/`.
* They expose domain tools such as nutrition planning, workouts, or progress tracking.
* Agents connect to MCP servers via stdio using `MCPToolClient` (defined in `agents/common.py`).
* Tools are invoked using:

  ```
  session.call_tool(...)
  ```

The result of tool execution is incorporated into the agent’s output plan.

Tool execution is isolated from orchestration logic, making it easy to swap domains without affecting coordination.

---

## Orchestrator

The `orchestrator/` service receives user requests and determines which coordinating agent should handle them.

In this example:

* The orchestrator routes requests to the `trainer_agent`.
* The trainer dynamically discovers and calls specialized agents (muscle, cardio, diet) based on capability.

The orchestrator does not contain domain logic. It only manages routing and coordination.

---

## Why This Architecture Scales

This repository uses fitness agents (muscle, cardio, diet, trainer) purely as an example.

The same architecture works across domains:

* Finance: risk, fraud, pricing, compliance agents
* Healthcare: triage, diagnostics, drug-check agents
* DevOps: incident, deployment, observability agents

To extend the system:

1. Add a new agent under `agents/`
2. Define its capabilities
3. Expose its `agent-card`
4. Register it with the registry on startup
5. Attach MCP tools if needed

No architectural redesign is required to move from 4 agents to N agents.

The system remains dynamically extensible.

---

## Runtime Documentation

Startup instructions, local execution flow, and quick test commands are available in `RUNNING.md`.

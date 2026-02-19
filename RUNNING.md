# Running The Platform

## Install

```bash
pip install -r requirements.txt
```

Optional environment variable:

```bash
REGISTRY_URL=http://localhost:8000
```

## Option A: One-click on Windows

Use:

```bat
start_all.bat
```

This opens separate terminals for:
- registry (`8000`)
- orchestrator (`8001`)
- muscle agent (`8002`)
- cardio agent (`8003`)
- diet agent (`8004`)
- trainer agent (`8005`)

MCP servers are started automatically by agents via stdio.

## Option B: Start manually

From repo root, open separate terminals and run:

```bash
uvicorn registry.main:app --port 8000
uvicorn orchestrator.main:app --port 8001
uvicorn agents.muscle_agent.main:app --port 8002
uvicorn agents.cardio_agent.main:app --port 8003
uvicorn agents.diet_agent.main:app --port 8004
uvicorn agents.trainer_agent.main:app --port 8005
```

## Quick Test

```bash
curl -X POST http://localhost:8001/plan \
  -H "Content-Type: application/json" \
  -d "{\"goal\":\"build muscle and endurance\",\"weight\":75}"
```

## Useful Checks

- Registry health: `http://localhost:8000/health`
- Registered cards: `http://localhost:8000/cards`
- Orchestrator health: `http://localhost:8001/health`


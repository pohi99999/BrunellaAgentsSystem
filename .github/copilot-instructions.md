# AI Coding Agent Instructions for BrunellaAgentSystem

Purpose: Help AI agents work effectively in this LangGraph fullstack repo.

## Architecture
- Hierarchical LangGraph with an Orchestrator and Tools.
  - Entrypoint graph: `backend/src/agent/graph.py` (exported as `graph`; referenced by `backend/langgraph.json`).
  - Tools: `backend/src/agent/tools.py` exposes:
    - `research_tool` → delegates to specialist research graph `backend/src/specialists/research_agent/`.
    - `qwen3_coder_tool` → delegates to `backend/src/specialists/coder_agent.py` (Ollama Qwen3 model).
  - Research specialist is a separate LangGraph (`research_agent/graph.py`), running a loop: generate_query → web_research → reflection → finalize_answer.
  - FastAPI app for HTTP: `backend/src/app.py`, mounted by LangGraph via `backend/langgraph.json`.
  - Frontend streams updates via LangGraph SDK: `frontend/src/App.tsx` connects to `/agent`.

## Dev Workflows
- Windows PowerShell venv (recommended):
  - Create: `py -3.11 -m venv .venv311`
  - Activate: `./.venv311/Scripts/Activate.ps1`
  - Install backend (editable): `pip install -e backend/[dev]`
  - LangGraph dev (explicit path if needed): `./.venv311/Scripts/langgraph.exe dev --config backend/langgraph.json`
  - Plain FastAPI fallback: `python run_server.py` (serves at `http://127.0.0.1:8000`).
- Frontend:
  - `cd frontend && npm install && npm run dev` (Vite on 5173).
- Root Make targets:
  - `make dev-backend` → `langgraph dev` in `backend/`.
  - `make dev-frontend` → Vite dev.
  - `make dev` → both.
- Backend tests and lint (within `backend/`): see Makefile uses `uv` runner.
  - `make test` or `uv run --with-editable . pytest`.
  - Lint/format: `make lint`, `make format` (ruff, mypy).

## Docker/Compose
- `docker-compose.yml` services: `backend`, `frontend`, `db` (Postgres), `redis`.
- Data on G: drive (repo-local) to avoid C: usage:
  - Postgres: `./docker-data/postgres:/var/lib/postgresql/data`
  - Redis: `./docker-data/redis:/data`
- Build cache optimization enabled in Dockerfiles (pip/poetry/npm BuildKit caches).
- Prod access:
  - Frontend served by Nginx on 3000, backend on 8000 (adjust `.env` and frontend `apiUrl` if needed).

## Config and Secrets
- Required: `GEMINI_API_KEY` (Google Gemini). Optional: `LANGSMITH_API_KEY`, `QWEN_API_KEY`.
- LangGraph config: `backend/langgraph.json` defines graphs and HTTP app.
- Research agent model knobs via env or config schema: see `backend/src/specialists/research_agent/configuration.py`.

## Patterns and Conventions
- Orchestrator delegates via tool-calling LLM (Gemini 1.5 Pro) to tools; tools call specialists.
- Research agent uses native Google Search tool via `google.genai` to get grounding metadata for citations; then composes final AIMessage.
- Coder agent uses Ollama (`qwen3:7b`) via `ChatOllama`; returns raw code only per system prompt.
- State schemas: orchestrator `AgentState` unions messages; research agent states in `research_agent/state.py`.
- Frontend submits with additional config fields (`initial_search_query_count`, `max_research_loops`, `reasoning_model`) that map to the research agent configuration.

## Extension Tips for Agents
- Adding a new specialist tool:
  1) Implement specialist in `backend/src/specialists/<name>/` and export runnable.
  2) Add a `@tool` wrapper in `backend/src/agent/tools.py`.
  3) Bind tool in `backend/src/agent/graph.py` via `llm.bind_tools([...])` and rebuild graph.
- Updating endpoints: edit `backend/src/app.py` and `backend/langgraph.json`.
- Frontend API target is chosen by `import.meta.env.DEV` in `frontend/src/App.tsx`.

## Known Gotchas
- Ensure `GEMINI_API_KEY` is set; `research_agent/graph.py` raises if missing.
- On Windows, prefer the repo-local venv `.venv311` and explicit path to `langgraph.exe`.
- Tests `backend/tests/test_api.py` reference `/crew` (legacy) — update or skip as needed.
- If Docker cannot access host Ollama (`host.docker.internal`), the coder tool may fail; adjust base_url or run without coder tool.

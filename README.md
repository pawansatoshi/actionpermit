# ActionPermit

**Autonomous authorization for AI-agent actions.**

ActionPermit is a Taskmaster-track submission for the All Things Agentic Hackathon. It demonstrates an agentic authorization workflow in which Gemini 3.5 Flash reasons about an action request, while a deterministic policy engine remains the security authority.

> **Gemini reasons. Deterministic policy authorizes. Evidence proves execution.**

## Workflow

`request → identity → credential → capability → scope → risk → policy → allow/deny → execute → verify → audit`

## Stack

- Gemini 3.5 Flash
- Google Agent Development Kit (ADK)
- FastAPI
- Cloud Run
- Responsive browser UI

## Security boundary

The LLM can classify and explain a request, but it cannot grant permission. Every side effect is gated by server-side deterministic policy checks. The default is deny.

## Local development

```bash
cd backend
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
uvicorn app.main:app --reload --port 8080
```

Open `http://localhost:8080`.

For Gemini-backed agent reasoning, set `GEMINI_API_KEY` server-side. The application still has a deterministic policy path for tests and safe fallback behavior.

## Tests

```bash
cd backend
pytest -q
```

## Cloud Run

Build from the repository root with `cloud/Dockerfile`. Configure `GEMINI_API_KEY` as a server-side Cloud Run secret/environment variable. Never place it in the frontend.

## Repository documents

- `docs/PROJECT_CONTRACT.md` — product and platform contract
- `docs/ARCHITECTURE.md` — system architecture and state machine
- `docs/THREAT_MODEL.md` — security model
- `docs/ADK_RISK_REGISTER.md` — ADK-specific risks and mitigations
- `docs/REQUIREMENT_MATRIX.md` — edge-case matrix
- `docs/RELEASE_GATE.md` — release criteria
- `docs/DAY0_STATUS.md` — verified/unverified hackathon assumptions

## Status

The repository is being built in phases. A release is not considered production-ready until the release gate is actually executed and recorded.

# ActionPermit

**Governed autonomous authorization for AI-agent actions.**

ActionPermit is a Taskmaster-track submission for the All Things Agentic Hackathon. Gemini provides reasoning through Google ADK, while a deterministic policy engine remains the security authority.

> **Gemini reasons. Deterministic policy authorizes. Evidence proves execution.**

## Workflow

`request → identity → credential → capability → scope → risk → policy → allow / approval / deny → execute → verify → audit`

## Stack

- Gemini 3.6 Flash (configurable server-side)
- Google Agent Development Kit (ADK)
- FastAPI
- Cloud Run
- Responsive browser UI

## Security boundary

The LLM cannot grant permission or directly invoke privileged side effects. Every action passes deterministic server-side authorization first. The default posture is deny. Approved actions execute only through registered executor capabilities, and successful execution requires verification.

## Demo action

The default `invoice.read` capability performs a real, registered read of the bundled invoice dataset. The executor does not accept arbitrary filesystem paths. Unauthorized actions never reach the executor.

## Local development

```bash
cd backend
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
uvicorn app.main:app --reload --port 8080
```

Open `http://localhost:8080`.

For Gemini-backed reasoning, set `GEMINI_API_KEY` or `GOOGLE_API_KEY` server-side. Authorization remains deterministic when model access is unavailable.

## Tests

```bash
cd backend
pytest -q
```

The CI workflow runs tests and builds the Cloud Run image on pushes and pull requests.

## Cloud Run

Build from the repository root with `cloud/Dockerfile`. A manual GitHub Actions deployment workflow is provided at `cloud/deploy.yml` and uses GitHub OIDC/Workload Identity Federation. Configure the Gemini credential as a server-side secret. Never place credentials in frontend JavaScript.

See `cloud/README.md` for deployment prerequisites and post-deployment verification.

## Architecture and demo

- `docs/ARCHITECTURE.md` — trust boundaries and lifecycle
- `docs/DEMO_SCRIPT.md` — four-minute Taskmaster demo
- `docs/RELEASE_CHECKLIST.md` — final engineering and submission gate

## Status

**Core implementation and security hardening complete.** Cloud Run packaging, deployment workflow, health/readiness checks, reproducibility tooling, architecture documentation, demo script, and release checklist are implemented. Actual Google Cloud deployment, live Gemini verification, and final release evidence remain before production-ready status can be declared.

# ActionPermit

**Governed autonomous authorization for AI-agent actions.**

ActionPermit is a Taskmaster-track submission for the All Things Agentic Hackathon. Gemini provides reasoning through Google ADK, while a deterministic policy engine remains the security authority.

> **Gemini reasons. Deterministic policy authorizes. Evidence proves execution.**

## Workflow

`request → identity → credential → capability → scope → risk → policy → allow / conditional / approval / deny → execute → verify → audit`

## Stack

- Gemini 3.6 Flash (configurable server-side)
- Google Agent Development Kit (ADK)
- FastAPI
- Cloud Run target
- Responsive browser UI

## Security boundary

The LLM cannot grant permission or directly invoke privileged side effects. Every action passes deterministic server-side authorization first. The default posture is deny. Approved actions execute only through registered executor capabilities, and successful execution requires verification.

## Decision model

- `ALLOW` — low-risk action may execute
- `ALLOW_WITH_CONDITIONS` — reserved for constrained policy extensions
- `REQUIRE_APPROVAL` — human authorization is required
- `DENY` — policy or risk blocks execution

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

GitHub Actions runs the backend test suite on pushes and pull requests.

## Cloud Run

Build from the repository root with `cloud/Dockerfile`. Configure the Gemini credential as a server-side Cloud Run secret/environment variable. Never place credentials in the frontend.

## Release discipline

A release is not considered production-ready until the complete release gate has been executed and recorded: tests, adversarial security checks, Cloud Run deployment verification, failure-path verification, reproducibility, and final demo verification.

## Status

**Core build in progress.** Policy, risk, approval, deterministic execution, audit events, ADK agent wiring, responsive workflow UI, and CI test automation are implemented. Deployment and independent release-gate verification remain before the project can be declared ready for final feature additions.

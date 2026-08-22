# 4-minute ActionPermit demo

## 0:00–0:30 — Problem
Show an AI agent requesting an action. Explain that an LLM should not be trusted to authorize its own privileged action.

## 0:30–1:15 — Deterministic authorization
Run a low-risk `invoice.read` request. Show identity, capability, scope, risk, policy decision and real registered execution.

## 1:15–2:00 — Human approval
Enable external + sensitive context. Show `REQUIRE_APPROVAL`. Approve it and show execution + verification.

## 2:00–2:45 — Security boundary
Send an unauthorized agent, excessive scope, dangerous action and path-like resource. Show `DENY` and no execution event.

## 2:45–3:20 — Evidence
Open the evidence/audit record and show policy, approval, execution and verification events tied to one evidence ID.

## 3:20–4:00 — Google Cloud proof
Show the Cloud Run service, deployment URL and logs. Explain that Gemini runs through Google ADK, while deterministic policy remains authoritative.

### Judge takeaway
`Gemini reasons → deterministic policy authorizes → registered executor acts → verification proves → evidence records.`

# Threat model

## Assets
Agent credentials, authorization policy, requests, execution evidence, Gemini API key, server state.

## Threats
Forged identity, credential mismatch, replay, duplicate execution, capability escalation, scope escalation, prompt injection, malicious tool descriptions, malformed input, secret leakage, fail-open authorization and stale state.

## Controls
1. Default deny.
2. LLM output is never authorization truth.
3. Server-side validation at every boundary.
4. Request IDs provide idempotency for repeated submissions.
5. Authorization occurs before side effects.
6. Verification failure cannot become success.
7. Secrets are server-side only.
8. Demo data is synthetic.

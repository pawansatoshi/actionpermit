# Architecture

```text
Browser
  -> Cloud Run / FastAPI
      -> Google ADK reasoner -> Gemini 3.5 Flash
      -> deterministic policy engine
          -> ALLOW -> sandbox executor -> verifier -> evidence
          -> DENY  -> evidence
```

Gemini is advisory. The deterministic policy engine is the security boundary. The executor in the hackathon build is synthetic and side-effect-free so the demonstration is safe and reproducible.

## State machine

RECEIVED -> VALIDATING -> IDENTITY_VERIFIED -> POLICY_EVALUATED -> AUTHORIZED | DENIED -> EXECUTING -> VERIFIED -> COMPLETED.

Failure states: FAILED, REJECTED, RETRYING, MISMATCH.

# Requirement matrix

Every feature is tested for normal, invalid, empty, missing, duplicate, replayed, timeout, network failure, unauthorized, malformed response, retry, refresh, direct URL, rapid interaction and concurrent request behavior.

Critical acceptance rules:

- unknown identity: DENY
- credential mismatch: DENY
- capability escalation: DENY
- scope escalation: DENY
- zero scope: DENY
- duplicate request ID: same decision/evidence response
- verification failure: no successful completion
- Gemini failure: authorization still follows deterministic policy

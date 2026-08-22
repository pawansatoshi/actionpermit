# ActionPermit Release Checklist

## Engineering

- [x] Deterministic policy engine
- [x] Identity and credential checks
- [x] Capability and scope enforcement
- [x] Risk scoring
- [x] Human approval gate
- [x] Approval replay protection
- [x] Approval request binding
- [x] Approval expiry / timeout
- [x] Registered executor
- [x] Execution verification
- [x] Evidence and audit trail
- [x] Tamper-evident audit event chain + integrity endpoint
- [x] Gemini + Google ADK boundary
- [x] Adversarial security suite
- [x] Health/readiness endpoints
- [x] Request correlation headers
- [x] Configurable CORS and security headers
- [x] Cloud Run Docker target
- [x] Reproducibility script

## Verification still required

- [ ] Latest CI run for the current release commit is SUCCESS
- [ ] Cloud Run deployment completed
- [ ] Cloud Run health/readiness verified
- [ ] Gemini production invocation verified
- [ ] Cloud Run failure paths verified
- [ ] Fresh-environment reproduction completed

## Hackathon

- [x] Taskmaster workflow is action-oriented
- [x] Gemini 3.5+ / configured Gemini model
- [x] Google agent framework: ADK
- [x] Google Cloud target: Cloud Run
- [x] Repository documentation
- [x] Architecture diagram
- [x] Demo script
- [ ] Cloud deployment proof captured
- [ ] Final demo video recorded
- [ ] Final submission write-up completed
- [ ] Final submission submitted

## Release rule

Do not call the project production-ready until every required verification item above is checked with actual evidence.

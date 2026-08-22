# Cloud Run deployment

The deployment workflow is intentionally manual (`workflow_dispatch`) so a deployment never happens accidentally on every push.

Required GitHub configuration:

- repository variable `GCP_PROJECT_ID`
- repository variable `GCP_REGION` (for example `us-central1`)
- repository secret `GCP_WIF_PROVIDER`
- repository secret `GCP_SERVICE_ACCOUNT`

The service account must be allowed to build/deploy Cloud Run from source. Configure the Gemini credential through Google Secret Manager or another server-side secret mechanism before enabling live Gemini reasoning. Never commit a Gemini key or place it in frontend JavaScript.

The workflow uses GitHub OIDC/Workload Identity Federation rather than a long-lived Google service-account key.

After deployment, verify:

1. Cloud Run service is `Ready`.
2. `/healthz` returns `{"status":"ok"}`.
3. `/readyz` returns `{"status":"ready"}`.
4. `/docs` loads.
5. A low-risk request reaches `COMPLETED`.
6. A high-risk request reaches `APPROVAL_REQUIRED`.
7. An unauthorized request reaches `DENIED` without execution.
8. Cloud Run logs show the request lifecycle and no secrets.

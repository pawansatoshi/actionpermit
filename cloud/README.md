# Cloud Run deployment

The deployment workflow is intentionally manual (`workflow_dispatch`) so a deployment never happens accidentally on every push.

## One-time Google Cloud setup

Required GitHub repository configuration:

- variable `GCP_PROJECT_ID`
- variable `GCP_REGION` (for example `us-central1`)
- secret `GCP_WIF_PROVIDER`
- secret `GCP_SERVICE_ACCOUNT`

Required Google Cloud resources/permissions:

- Cloud Run API enabled
- Artifact Registry API enabled
- Cloud Build API enabled
- Secret Manager API enabled
- Artifact Registry Docker repository named `actionpermit` in the selected region (the workflow creates it if the deployer can do so)
- Secret Manager secret named `actionpermit-gemini-api-key` containing the Gemini API key
- the Cloud Run runtime service account must have `roles/secretmanager.secretAccessor` on that Gemini secret
- the GitHub deployment service account must be permitted to build/push images and deploy Cloud Run

The workflow uses GitHub OIDC/Workload Identity Federation rather than a long-lived Google service-account key.

## Deployment

Run the `deploy-cloud-run` workflow manually from GitHub Actions. It:

1. authenticates using OIDC
2. ensures the Artifact Registry repository exists
3. builds `cloud/Dockerfile`
4. pushes an immutable image tagged with the Git commit SHA
5. deploys that image to Cloud Run
6. injects the Gemini key from Secret Manager
7. retrieves the Cloud Run URL
8. verifies `/healthz`, `/readyz`, and `/`

## Live verification gate

A deployment is not considered Phase 21 complete until all of these are verified:

1. Cloud Run revision is `Ready`.
2. `/healthz` returns `{"status":"ok"}`.
3. `/readyz` returns `{"status":"ready"}`.
4. `/docs` loads.
5. Gemini-backed reasoning executes successfully.
6. A low-risk request reaches `COMPLETED`.
7. A high-risk request reaches `APPROVAL_REQUIRED`.
8. An unauthorized request reaches `DENIED` without execution.
9. Audit evidence is retrievable.
10. Cloud Run logs show the lifecycle without exposing secrets.

Never commit a Gemini key or place credentials in frontend JavaScript.

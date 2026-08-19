#!/usr/bin/env bash
set -euo pipefail
: "${PROJECT_ID:?Set PROJECT_ID}"
: "${REGION:?Set REGION}"
SERVICE="actionpermit"
IMAGE="${REGION}-docker.pkg.dev/${PROJECT_ID}/actionpermit/${SERVICE}:latest"

gcloud auth configure-docker "${REGION}-docker.pkg.dev" --quiet
gcloud builds submit --tag "$IMAGE" .
gcloud run deploy "$SERVICE" --image "$IMAGE" --region "$REGION" --project "$PROJECT_ID" --platform managed --set-env-vars "GEMINI_MODEL=gemini-3.5-flash" --allow-unauthenticated

gcloud run services describe "$SERVICE" --region "$REGION" --project "$PROJECT_ID" --format='value(status.url)'

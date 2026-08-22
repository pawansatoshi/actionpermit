#!/usr/bin/env bash
set -euo pipefail
cd "$(dirname "$0")/.."
python -m pip install -r backend/requirements.txt
PYTHONPATH="$PWD/backend" python -m pytest -q
docker build -f cloud/Dockerfile -t actionpermit:verify .
echo "ActionPermit reproducibility verification passed"

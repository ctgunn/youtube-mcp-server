#!/usr/bin/env bash

set -euo pipefail

ROOT_DIR="$(CDPATH="" cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"

required_vars=(
  PROJECT_ID
  REGION
  SERVICE_NAME
  IMAGE_REFERENCE
  SERVICE_ACCOUNT_EMAIL
  MCP_ENVIRONMENT
  MIN_INSTANCES
  MAX_INSTANCES
  CONCURRENCY
  TIMEOUT_SECONDS
)

for key in "${required_vars[@]}"; do
  if [[ -z "${!key:-}" ]]; then
    echo "Missing required environment variable: ${key}" >&2
    exit 1
  fi
done

if [[ "${MCP_ENVIRONMENT}" != "dev" && "${MCP_ENVIRONMENT}" != "staging" && "${MCP_ENVIRONMENT}" != "prod" ]]; then
  echo "MCP_ENVIRONMENT must be one of dev, staging, prod" >&2
  exit 1
fi

if [[ "${MCP_ENVIRONMENT}" == "staging" || "${MCP_ENVIRONMENT}" == "prod" ]]; then
  : "${SECRET_REFERENCES:=YOUTUBE_API_KEY}"
else
  : "${SECRET_REFERENCES:=}"
fi

export PYTHONPATH="${ROOT_DIR}/src:${PYTHONPATH:-}"
export MCP_SERVER_IMPLEMENTATION="${MCP_SERVER_IMPLEMENTATION:-uvicorn}"
export MCP_ASGI_APP="${MCP_ASGI_APP:-mcp_server.cloud_run_entrypoint:app}"

# The resulting deployment record is the expected input for the
# session-aware streamable transport verifier in
# scripts/verify_cloud_run_foundation.py.

python3 - <<'PY'
from mcp_server.deploy import (
    deployment_input_from_mapping,
    execute_deploy_command,
    serialize_deployment_run,
)
import json
import os
import sys

settings = deployment_input_from_mapping(os.environ)
record = execute_deploy_command(
    settings,
    gcloud_bin=os.environ.get("GCLOUD_BIN", "gcloud"),
)
print(json.dumps(serialize_deployment_run(record)))
raise SystemExit(0 if record.outcome == "success" else 1)
PY

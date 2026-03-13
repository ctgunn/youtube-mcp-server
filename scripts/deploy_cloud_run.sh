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

python3 - <<'PY'
from mcp_server.deploy import build_deploy_command, deployment_input_from_mapping
import os

settings = deployment_input_from_mapping(os.environ)
command = build_deploy_command(settings)
print(" ".join(command))
PY

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
  if [[ -z "${!key:-}" && -z "${INFRA_OUTPUTS_FILE:-}" ]]; then
    echo "Missing required environment variable: ${key}" >&2
    exit 1
  fi
done

if [[ -n "${MCP_ENVIRONMENT:-}" && "${MCP_ENVIRONMENT}" != "dev" && "${MCP_ENVIRONMENT}" != "staging" && "${MCP_ENVIRONMENT}" != "prod" ]]; then
  echo "MCP_ENVIRONMENT must be one of dev, staging, prod" >&2
  exit 1
fi

if [[ "${MCP_ENVIRONMENT:-}" == "staging" || "${MCP_ENVIRONMENT:-}" == "prod" ]]; then
  : "${SECRET_REFERENCES:=YOUTUBE_API_KEY,MCP_AUTH_TOKEN}"
else
  : "${SECRET_REFERENCES:=}"
fi

export PYTHONPATH="${ROOT_DIR}/src:${PYTHONPATH:-}"
export MCP_SERVER_IMPLEMENTATION="${MCP_SERVER_IMPLEMENTATION:-uvicorn}"
export MCP_ASGI_APP="${MCP_ASGI_APP:-mcp_server.cloud_run_entrypoint:app}"
export MCP_SECRET_ACCESS_MODE="${MCP_SECRET_ACCESS_MODE:-secret_manager_env}"
export MCP_SECRET_REFERENCE_NAMES="${MCP_SECRET_REFERENCE_NAMES:-${SECRET_REFERENCES:-}}"
export PUBLIC_INVOCATION_INTENT="${PUBLIC_INVOCATION_INTENT:-private_only}"
export MCP_AUTH_REQUIRED="${MCP_AUTH_REQUIRED:-}"
export MCP_ALLOWED_ORIGINS="${MCP_ALLOWED_ORIGINS:-}"
export MCP_ALLOW_ORIGINLESS_CLIENTS="${MCP_ALLOW_ORIGINLESS_CLIENTS:-}"
export MCP_SESSION_BACKEND="${MCP_SESSION_BACKEND:-}"
export MCP_SESSION_STORE_URL="${MCP_SESSION_STORE_URL:-}"
export MCP_SESSION_CONNECTIVITY_MODEL="${MCP_SESSION_CONNECTIVITY_MODEL:-}"
export MCP_SESSION_NETWORK_REFERENCE="${MCP_SESSION_NETWORK_REFERENCE:-}"
export MCP_SESSION_SUBNET_REFERENCE="${MCP_SESSION_SUBNET_REFERENCE:-}"
export MCP_SESSION_CONNECTOR_REFERENCE="${MCP_SESSION_CONNECTOR_REFERENCE:-}"
export MCP_SESSION_DURABILITY_REQUIRED="${MCP_SESSION_DURABILITY_REQUIRED:-}"
export MCP_SESSION_TTL_SECONDS="${MCP_SESSION_TTL_SECONDS:-}"
export MCP_SESSION_REPLAY_TTL_SECONDS="${MCP_SESSION_REPLAY_TTL_SECONDS:-}"

# The resulting deployment record is the expected input for the
# session-aware streamable transport verifier in
# scripts/verify_cloud_run_foundation.py.

python3 - <<'PY'
from mcp_server.deploy import (
    iac_outputs_to_mapping,
    load_iac_outputs_file,
    merge_deployment_values,
    deployment_input_from_mapping,
    execute_deploy_command,
    serialize_deployment_run,
)
import json
import os
import sys
from pathlib import Path

values = dict(os.environ)
infra_outputs_file = values.get("INFRA_OUTPUTS_FILE", "").strip()
if infra_outputs_file:
    values = merge_deployment_values(
        iac_outputs_to_mapping(load_iac_outputs_file(infra_outputs_file)),
        values,
    )
settings = deployment_input_from_mapping(values)
record = execute_deploy_command(
    settings,
    gcloud_bin=os.environ.get("GCLOUD_BIN", "gcloud"),
)
payload = json.dumps(serialize_deployment_run(record))
output_path = values.get("DEPLOYMENT_RECORD_FILE", "").strip()
if output_path:
    path = Path(output_path)
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(payload)
print(payload)
raise SystemExit(0 if record.outcome == "success" else 1)
PY

#!/usr/bin/env bash

set -euo pipefail

ROOT_DIR="$(CDPATH="" cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
ENV_FILE="${ROOT_DIR}/.env.local"

if [[ ! -f "${ENV_FILE}" ]]; then
  echo "Missing ${ENV_FILE}. Restore the local runtime defaults file before running local dev." >&2
  exit 1
fi

set -a
source "${ENV_FILE}"
set +a

export PYTHONPATH="${PYTHONPATH:-src}"

if [[ "${LOCAL_SESSION_MODE:-minimal}" == "hosted" ]]; then
  export MCP_SESSION_BACKEND=redis
  export MCP_SESSION_STORE_URL="${MCP_SESSION_STORE_URL:-redis://127.0.0.1:${LOCAL_REDIS_PORT:-6379}/0}"
  export MCP_SESSION_CONNECTIVITY_MODEL=local_docker_compose
  export MCP_SESSION_DURABILITY_REQUIRED=true
fi

cd "${ROOT_DIR}"
exec python3 -m uvicorn mcp_server.cloud_run_entrypoint:app --host "${HOST:-0.0.0.0}" --port "${PORT:-8080}"

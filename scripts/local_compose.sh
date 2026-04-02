#!/usr/bin/env bash

set -euo pipefail

ROOT_DIR="$(CDPATH="" cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
COMPOSE_FILE="${ROOT_DIR}/infrastructure/local/compose.yaml"

if command -v docker >/dev/null 2>&1 && docker compose version >/dev/null 2>&1; then
  exec docker compose -f "${COMPOSE_FILE}" "$@"
fi

if command -v docker-compose >/dev/null 2>&1; then
  exec docker-compose -f "${COMPOSE_FILE}" "$@"
fi

if command -v podman >/dev/null 2>&1 && podman compose version >/dev/null 2>&1; then
  exec podman compose -f "${COMPOSE_FILE}" "$@"
fi

if command -v podman-compose >/dev/null 2>&1; then
  exec podman-compose -f "${COMPOSE_FILE}" "$@"
fi

echo "No supported compose command was found." >&2
echo "Install Docker Compose or Podman Compose, or run the local dependency stack manually." >&2
exit 1

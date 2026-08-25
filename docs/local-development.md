# Local development

Use this guide for day-to-day development, local testing, and optional
Redis-backed session testing. It is deliberately independent of GCP
provisioning.

## Prerequisites

- Python 3.11 or newer
- `pip`
- `make`
- Docker Compose or Podman Compose only for the hosted-like Redis path

Create an isolated environment and install the declared development tools:

```bash
python3 -m venv .venv
source .venv/bin/activate
python -m pip install --upgrade pip
python -m pip install -e '.[dev]'
```

## Minimal local runtime path

The minimal local runtime path does not require cloud provisioning, Docker, or
Redis. It is the fastest path for normal feature work.

Create your private local configuration from the tracked example:

```bash
cp .env.example .env.local
```

Review `.env.local` and add local-only values as needed. Never commit it or
put production credentials in it. `YOUTUBE_API_KEY` is needed only when you
intend to exercise live YouTube API calls.

Run the repository quality gate before changing or starting the service:

```bash
make quality
bash scripts/dev_local.sh
```

The local runtime defaults are loaded from `.env.local`. In a second terminal,
confirm the process is healthy and ready:

```bash
curl http://127.0.0.1:8080/health
curl http://127.0.0.1:8080/ready
```

## Local MCP verification

The server exposes MCP over `/mcp`. Use the normal MCP initialize handshake
from a compatible client, or follow the complete request examples in the
[architecture guide](./architecture.md#one-request-lifecycle).

For code changes, the quality gate is the required baseline:

```bash
make lint
make typecheck
make test
make quality
```

`make quality` runs all three checks in sequence and is the canonical command
used by local development and release automation.

## Hosted-like local verification path

Use this path only when testing durable sessions, reconnect behavior, event
replay, or readiness behavior backed by Redis. It is still local development;
it does not involve Cloud Run, GCP IAM, or public reachability.

```bash
./scripts/local_compose.sh up -d
LOCAL_SESSION_MODE=hosted bash scripts/dev_local.sh
```

When finished, stop the supporting dependency:

```bash
./scripts/local_compose.sh down
```

For the runtime modes, Redis configuration, and troubleshooting, see the
[local infrastructure README](../infrastructure/local/README.md).

## What belongs where

- Use `.env.local` for private, machine-specific local configuration.
- Use `infrastructure/local/.env.example` for tracked hosted-like local
  overrides only.
- Use Secret Manager for hosted application values.
- Use the [hosted deployment guide](./hosted-deployment.md) for GCP and
  GitHub Actions configuration.

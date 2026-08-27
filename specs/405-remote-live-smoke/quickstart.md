# Layer 4 Remote MCP Read-Only Live Smoke Quickstart

## 1. Prepare a safe operator environment

From the repository root, install development dependencies if needed:

```bash
python -m pip install -e '.[dev]'
```

Use only an approved staging or production MCP endpoint. Do not place API keys, MCP tokens, authorization headers, session identifiers, private identifiers, request arguments, or upstream response bodies in checked-in files, shell history, logs, or review evidence.

## 2. Understand the verification boundary

| Workflow | Command | Purpose | External live calls |
| --- | --- | --- | --- |
| Catalog verification | `make test-tools` | Deterministically checks discovery and public-route coverage for the default catalog. | No |
| Configured-runtime verification | `make test-runtime` | Deterministically checks configured YouTube capability paths through MCP with controlled requests. | No |
| Local live smoke | `make test-live-smoke` | Manually checks the local configured application with a real YouTube API key. | Yes, to YouTube only |
| Remote live smoke | `make test-remote-live-smoke` | Manually checks an already running remote MCP endpoint, its session/authentication path, selected handlers, and YouTube execution. | Yes, to the remote endpoint and its configured upstream |

Remote live smoke is not a replacement for the first three workflows. It consumes quota, depends on endpoint and upstream availability, and is never an ordinary pull-request, quality, CI, or automated deployment check.

## 3. Run deterministic pre-merge evidence

```bash
PYTHONPATH=src python3 -m pytest tests/integration/test_remote_mcp_live_smoke.py
make test-tools
make test-runtime
make test
```

These checks use only controlled test responders and must not need a real endpoint or credentials.

## 4. Run the authorized remote smoke after deployment

Set only the values required by the approved endpoint. A bearer token is required only when that endpoint enforces bearer authentication.

```bash
RUN_REMOTE_MCP_LIVE_SMOKE=1 \
REMOTE_MCP_URL='approved-remote-mcp-url' \
MCP_AUTH_TOKEN='operator-supplied-value' \
REMOTE_MCP_AUTH_REQUIRED=1 \
make test-remote-live-smoke
```

The aggregate command runs Layer 2 and Layer 3 in separate bounded MCP
sessions, then prints an overall summary. Run an individual layer when needed:

```bash
make test-remote-layer2-live-smoke
make test-remote-layer3-live-smoke
```

The Layer 3 command invokes only the reviewed 10-tool API-key-compatible composed allowlist.
Transcript/caption workflows and higher-cost search/enrichment fan-out remain
out of scope for this suite.

Set `REMOTE_MCP_AUTH_REQUIRED=1` only when the approved endpoint requires
bearer authentication; then `MCP_AUTH_TOKEN` is mandatory before any request.

Expected safe evidence:

- initialization followed by remote catalog discovery and only reviewed selected calls;
- one compact terminal safe outcome per selected tool plus an aggregate count of intentionally excluded discovered tools;
- a maximum of 12 tool calls, plus initialization and discovery, with finite timeouts;
- verified endpoint identity and top-level item count only for successful structured results; and
- no credential, authorization header, session ID, request argument, raw exception, or upstream body.

If required enablement, endpoint, or endpoint authentication is absent, the command must fail before remote activity. Do not paste an output that may contain sensitive information into an issue or pull request; share only the command's redacted report.

## 5. Handle outcomes safely

- `success`: record the safe tool name, verified endpoint identity, and item count; no further data is needed.
- `safe_availability_error`: record the stable category only, then review public-data or upstream availability outside the evidence artifact.
- `actionable_failure`: verify endpoint authorization, deployment health, session continuity, timeout, and upstream status privately; correct the condition before a new authorized run.
- `excluded`: do not bypass the explicit allowlist. Propose a separately reviewed public fixture and allowlist update if a new live-safe tool is needed.
- `bound_reached`: do not increase limits ad hoc. Review the allowlist and quota/safety implications before changing the documented bound.

## 6. Run the constitutional completion gate

After all implementation and documentation changes, run:

```bash
make quality
```

This runs linting, type checking, and the complete test suite. Fix every failure before marking the feature complete. Do not add the authorized remote smoke to this command.

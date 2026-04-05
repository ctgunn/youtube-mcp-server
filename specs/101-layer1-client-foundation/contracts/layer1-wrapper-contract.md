# Contract: YT-101 Layer 1 Wrapper Contract

## Purpose

Define the internal contract that every Layer 1 YouTube wrapper must satisfy so future endpoint slices can add coverage without redefining transport, authentication, observability, retry, quota, or failure semantics.

## Contract Scope

- Internal-only Layer 1 wrapper behavior
- Shared request execution
- Auth mode declaration and credential expectations
- Retry and backoff hooks
- Logging hooks
- normalized upstream failures
- Higher-layer typed consumption expectations

This contract does not define new public MCP tools or hosted endpoint behavior.
The representative implementation for this contract lives under `/Users/ctgunn/Projects/youtube-mcp-server/src/mcp_server/integrations/`.

## Wrapper Requirements

Every Layer 1 wrapper must declare:

- `resource_name`
- `operation_name`
- `http_method`
- `path_shape`
- `request_shape`
- `auth_mode`
- `quota_cost`
- `lifecycle_state` when deprecation, limited availability, or doc inconsistencies matter

Every Layer 1 wrapper must use:

- One shared request executor
- One shared auth policy surface
- One shared retry classification surface
- One shared logging hook boundary
- One shared upstream error normalizer

## Auth Mode Contract

Supported auth modes:

- `api_key`: Wrapper can execute with API-key-based credentials
- `oauth_required`: Wrapper requires OAuth credentials
- `conditional`: Wrapper auth expectation depends on request or caller context and must document the condition

Wrappers must not infer auth requirements implicitly from ad hoc code paths. The declared auth mode must be reviewable from the wrapper contract itself.

## Retry and Error Contract

Wrappers must rely on shared retry and backoff policies rather than per-wrapper retry implementations.

Normalized failures must provide:

- `category`
- `message`
- `retryable`
- safe upstream context when available

Raw upstream failure payloads must not become the higher-layer contract.

## Observability Contract

The shared execution path must provide a consistent place to record:

- request identity
- wrapper identity
- auth mode
- normalized outcome
- latency

Sensitive values such as secrets or tokens must not be emitted in logs.

## Higher-Layer Consumption Contract

Higher-layer workflows must consume typed Layer 1 methods rather than construct raw upstream requests themselves.

Representative proof for YT-101 must show:

- one wrapper can be defined through the shared contract
- one higher-layer consumer can depend on the typed wrapper method
- normalized failures remain stable for the consumer

## Review and Validation Expectations

- Unit tests cover metadata validation, auth mode handling, retry classification, and failure normalization
- Integration tests cover representative wrapper execution via the shared request contract
- Contract tests cover the representative higher-layer consumer boundary
- All new or changed Python functions implementing this contract must include reStructuredText docstrings
- Final feature completion requires `python3 -m pytest` from `/Users/ctgunn/Projects/youtube-mcp-server` and `ruff check .`

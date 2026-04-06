# Contract: YT-103 `activities.list` Layer 1 Wrapper Contract

## Purpose

Define the internal contract that the endpoint-specific `activities.list` wrapper must satisfy so maintainers and future higher-layer authors can use the endpoint through one typed Layer 1 method without re-deriving auth, quota, or filter rules from raw upstream semantics.

The representative implementation for this contract will live under `/Users/ctgunn/Projects/youtube-mcp-server/src/mcp_server/integrations/activities.py`.

## Contract Scope

- Internal-only Layer 1 wrapper behavior for `activities.list`
- Endpoint identity and quota visibility
- Supported filter-selection modes
- Public versus authorized-user auth expectations
- Empty-result handling
- Shared executor, observability, and normalized-failure reuse

This contract does not define a new public MCP tool or a hosted-route change.

## Wrapper Requirements

The `activities.list` wrapper must declare:

- `resource_name` as `activities`
- `operation_name` as `list`
- `http_method`
- `path_shape`
- `request_shape`
- `auth_mode`
- `quota_cost`
- `auth_condition_note`

The wrapper must use:

- the shared `EndpointMetadata` contract
- the shared `EndpointRequestShape` validation surface
- the shared `IntegrationExecutor`
- the shared auth context model
- the shared normalized-failure behavior
- the shared observability hooks

## Supported Request Modes

The wrapper contract must make the following modes reviewable:

- `channelId`: public channel activity retrieval
- `mine`: authorized-user retrieval for the caller's own activity feed
- `home`: authorized-user retrieval for the caller's home activity feed

Rules:

- `part` is required for every supported request
- exactly one supported request mode may be selected
- mixed mode combinations are invalid for this slice
- unsupported or unexpected request fields are rejected unless the wrapper contract is explicitly expanded

## Auth Contract

The wrapper must expose `mixed/conditional` auth behavior to maintainers because auth expectations vary by filter mode.

The maintainer-facing auth explanation must state:

- channel-based retrieval is available through the public access path
- `mine` and `home` require authorized user context
- higher-layer consumers must choose the request mode before choosing the auth path

The wrapper must not leave these distinctions implicit in runtime code alone.

## Success and Error Semantics

Successful outcomes must include:

- a structured result payload for valid requests
- zero or more activity items
- stable wrapper identity, quota, and auth context available through metadata or derived review surfaces

Error handling rules:

- unsupported mode combinations are rejected before transport execution
- missing required fields are rejected before transport execution
- upstream failures flow through the shared normalized-failure path
- empty valid results are not treated as failures

## Observability and Security

- The wrapper must execute through the shared executor so request, response, and error events stay visible through the existing observability hooks.
- Auth-mode decisions may be logged as safe metadata, but secrets, tokens, and raw credential values must not appear in logs or contract artifacts.

## Validation Expectations

Representative proof for YT-103 must show:

- the endpoint-specific wrapper can execute a supported channel-based request through the shared executor
- the wrapper exposes quota cost `1` and `mixed/conditional` auth guidance in maintainer-facing artifacts
- invalid mixed filter combinations are rejected deterministically
- valid empty results remain successful outcomes

Required coverage:

- unit tests for request validation and metadata completeness
- contract tests for wrapper-facing documentation and reuse expectations
- integration tests for supported public and authorized-user execution paths

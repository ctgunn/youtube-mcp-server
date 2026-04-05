# Contract: YT-102 Layer 1 Metadata Standard

## Purpose

Define the internal metadata standard that every representative Layer 1 wrapper must satisfy so maintainers can identify endpoint identity, quota cost, auth expectations, and lifecycle caveats directly from wrapper-facing artifacts.

The representative implementation for this contract will remain under `/Users/ctgunn/Projects/youtube-mcp-server/src/mcp_server/integrations/`.

## Contract Scope

- Internal-only Layer 1 wrapper metadata
- Maintainer-facing quota visibility
- Maintainer-facing auth expectation visibility
- Lifecycle and documentation caveat recording
- Reviewer validation of metadata completeness

This contract does not define new public MCP tools, new hosted endpoints, or changes to MCP transport behavior.

## Required Metadata Fields

Every representative Layer 1 wrapper in scope must expose:

- `resource_name`
- `operation_name`
- `http_method`
- `path_shape`
- `request_shape`
- `auth_mode`
- `quota_cost`
- `lifecycle_state`
- `caveat_note` when lifecycle review context is required
- `auth_condition_note` when auth is mixed or conditional

Every representative wrapper must also expose:

- a maintainer-visible quota reference in a signature, reStructuredText docstring, or adjacent implementation comment
- a maintainer-visible auth explanation when auth is mixed or conditional
- a maintainer-visible caveat note when lifecycle state indicates deprecation, limited availability, or official-document inconsistency

## Auth Metadata Rules

Supported wrapper auth modes are:

- `api_key`
- `oauth_required`
- `mixed/conditional`

Rules:

- Wrappers using one stable auth expectation may declare that mode directly.
- Wrappers whose auth expectation changes by request, caller context, or account state must declare `mixed/conditional`.
- `mixed/conditional` metadata is incomplete unless it includes a maintainer-facing `auth_condition_note` explaining when auth expectations change.
- Runtime execution details must not replace the wrapper-level auth explanation required for review.

## Quota Metadata Rules

- `quota_cost` must record the official quota-unit cost used for planning and review.
- Quota metadata must be visible without consulting upstream documentation.
- Missing, zero, or hidden quota metadata makes the wrapper incomplete for YT-102 purposes.
- If official quota guidance changes or conflicts across sources, the wrapper must preserve the chosen quota record and include a caveat note that explains the discrepancy.

## Lifecycle and Caveat Rules

Representative wrappers must make caveats explicit when any of the following apply:

- the endpoint is deprecated
- the endpoint is availability-limited
- the endpoint has conflicting or unclear official documentation

Required caveat behavior:

- `lifecycle_state` identifies the broad lifecycle condition
- a `caveat_note` explains the maintainer-relevant implication
- the caveat is visible in a contract artifact, wrapper docstring, or adjacent implementation note

Generic optional notes are not sufficient when one of these caveat categories applies.

## Review Validation Expectations

The feature must prove that maintainers can:

- identify a representative wrapper's endpoint identity in one review pass
- identify quota cost in under 30 seconds from wrapper-facing artifacts
- determine whether auth is stable or mixed/conditional without reading upstream docs
- find lifecycle and documentation caveats without rediscovering them manually

Validation must include:

- unit tests for metadata completeness and conditional requirements
- contract tests for maintainer-facing contract artifacts
- integration checks showing representative wrappers can still be compared and consumed through the existing Layer 1 foundation

## Invariants

- The metadata standard extends the YT-101 foundation rather than replacing it
- No new public MCP contract is introduced by this feature
- New or changed Python functions involved in the metadata standard must include reStructuredText docstrings
- Sensitive credential values must never appear in metadata artifacts, tests, or logs

# Contract: YT-156 Layer 1 Response Normalizer Dispatch

## Purpose

Define the internal response-normalizer dispatch contract for replacing the broad operation-key conditional response handling with explicit resource-family-owned mappings while preserving every existing response shape.

This contract is internal to the Layer 1 YouTube integration path and does not define a public MCP interface.

## Contract Scope

- Operation-key to response-normalizer registration
- Resource-family ownership for endpoint-specific response handling
- Fallback parsing behavior for operations without specialized normalizers
- Preservation of successful payload shapes and normalized failure behavior

This contract does not change request construction, credential attachment, upstream execution, retry behavior, or public MCP results.

## Dispatch Expectations

The dispatch mechanism must:

- select specialized normalizers by stable `operation_key`
- keep operation-to-normalizer ownership explicit and reviewable
- allow resource-family modules to register the normalizers they own
- accommodate normalizers that require execution context only, payload only, or both execution context and payload
- preserve generic JSON object parsing when no specialized normalizer is registered
- keep no-content acknowledgement handling equivalent for existing mutation endpoints, including handlers that do not parse response payloads
- keep upload, download, list, update, delete, rating, reporting, search, and localization response shapes equivalent to the established Layer 1 contracts

The dispatch mechanism may be implemented as an explicit registry, mapping, or similarly auditable structure. It must not rely on silent dynamic behavior that hides missing or misspelled operation keys from review.

## Failure Boundary Expectations

The refactor must preserve:

- local validation failures before execution
- access-related failures
- normalized upstream refusal failures
- rate-limit and quota-related failures
- upstream unavailable failures
- successful no-content acknowledgement outcomes
- generic response parsing failures for non-object payloads where currently applicable

The dispatch change must not alter credential attachment, upstream error normalization, status code handling, retry behavior, or observability hook behavior.

## Review Validation Expectations

Validation must prove that:

- representative operation keys map to the same successful response shape as before the refactor
- operations without specialized handling still use the same generic object parsing behavior
- no-content mutation acknowledgements remain distinct from empty or ambiguous responses
- response normalizer ownership is visible by resource family
- missing or unsupported operation keys fail or fall back in the same manner as the established contract
- `mcp_server.integrations.youtube` continues to expose existing transport and request-building helpers
- new or changed Python normalizer and dispatch functions include reStructuredText docstrings

## Invariants

- The refactor may change where response normalizers live, not what they return
- Specialized response normalizers remain endpoint-specific where endpoint behavior requires it
- Generic YouTube transport behavior remains shared
- No secrets, OAuth tokens, API keys, raw media payloads, or delegated-owner credentials may appear in normalized response artifacts or tests

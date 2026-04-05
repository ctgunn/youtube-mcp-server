# Research: YT-101 Layer 1 Shared Client Foundation

## Decision: Keep the Layer 1 foundation internal under a dedicated integration-oriented module

**Rationale**: The repository already separates transport, protocol, observability, and tool concerns. Placing shared YouTube integration behavior under a dedicated internal module preserves that boundary and avoids mixing MCP-facing tool behavior with upstream client logic.

**Alternatives considered**:

- Extend `src/mcp_server/tools/` to hold upstream client behavior. Rejected because it mixes public tool concerns with internal integration concerns.
- Put the foundation under `transport/`. Rejected because transport is already focused on MCP communication rather than upstream provider access.

## Decision: Use a metadata-first wrapper contract

**Rationale**: YT-101 and YT-102 both require wrappers to declare endpoint identity, request shape, auth mode, quota cost, and lifecycle notes consistently. A metadata-first contract keeps later endpoint additions mostly declarative and easier to review.

**Alternatives considered**:

- Hand-written wrapper methods with embedded request details. Rejected because they duplicate logic and make quota/auth review inconsistent.
- Defer metadata strictness to YT-102. Rejected because the contract shape should be established before the endpoint inventory grows.

## Decision: Model auth expectations explicitly as `api_key`, `oauth_required`, and `conditional`

**Rationale**: The seed plan explicitly calls out these modes. Treating them as first-class contract values makes higher-layer behavior easier to reason about and avoids ambiguous boolean flags.

**Alternatives considered**:

- Simple booleans such as `requires_oauth`. Rejected because mixed or conditional cases do not fit clearly.
- Free-form strings with no validation. Rejected because maintainers would lose review-time consistency.

## Decision: Keep retry and backoff policy-based and opt-in

**Rationale**: Some upstream failures are transient, while others should fail fast. Policy-based retries let wrappers share behavior without forcing unsafe automatic retries on non-retryable failures.

**Alternatives considered**:

- Retry all failures automatically. Rejected because it can hide invalid requests and complicate quota behavior.
- Leave retry rules entirely per-wrapper. Rejected because it recreates the inconsistency YT-101 is meant to eliminate.

## Decision: Normalize upstream failures into a small internal error taxonomy

**Rationale**: Higher layers need a stable failure model that is independent of raw upstream formats, but maintainers still need source category and retryability context for debugging and recovery.

**Alternatives considered**:

- Pass through upstream failures unchanged. Rejected because it couples callers to provider-specific payloads.
- Collapse all failures into one generic error. Rejected because it removes useful signals for retries, auth handling, and review.

## Decision: Put logging hooks at the shared executor boundary

**Rationale**: The executor is the narrowest reusable point where request identity, endpoint metadata, auth mode, normalized status, and latency can be captured consistently across all wrappers.

**Alternatives considered**:

- Log inside each wrapper. Rejected because coverage becomes inconsistent and repetitive.
- Skip dedicated hooks and rely only on outer MCP logs. Rejected because future maintainers would lose visibility into upstream execution behavior.

## Decision: Prove the foundation with one representative wrapper and one representative higher-layer consumer

**Rationale**: YT-101 is a foundational slice, not the full endpoint inventory. One wrapper validates the maintainer experience, and one consumer validates the higher-layer seam without inflating scope.

**Alternatives considered**:

- Add multiple endpoint wrappers immediately. Rejected because it mixes foundation work with endpoint expansion.
- Design without representative proof points. Rejected because the foundation would be harder to verify before YT-102 and later slices.

## Decision: Align tests to the existing `unit`, `integration`, and `contract` layers

**Rationale**: The repository already uses those three layers, and the constitution requires integration and regression coverage in addition to unit coverage.

**Alternatives considered**:

- Unit tests only. Rejected because boundary behavior between metadata, execution, and higher-layer reuse is the main risk.
- End-to-end hosted validation for YT-101. Rejected because this feature is internal-only and does not change hosted MCP behavior directly.

## Decision: Require reStructuredText docstrings on all new integration foundation functions

**Rationale**: The constitution requires them, and maintainers will extend this foundation repeatedly across the YT-1xx series.

**Alternatives considered**:

- Rely only on type hints and tests. Rejected because project governance explicitly requires docstrings.
